-- Schema per il clone del modulo Scrum (nome provvisorio: "Officina").
-- Postgres 15+ / Supabase. Tutti i dati appartengono a un'organizzazione (org_id).
-- Accesso: Row Level Security su org_id tramite la tabella memberships.
-- Tempi di lavoro in minuti interi; istanti in timestamptz (UTC); settimane come
-- data del lunedì ISO (week_start).

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- utility
create or replace function set_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

-- ---------------------------------------------------------------- tenancy
create table orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique check (slug ~ '^[a-z0-9-]{2,40}$'),
  timezone text not null default 'Europe/Rome',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Su Supabase user_id referenzia auth.users(id). Qui una tabella locale per
-- poter validare lo schema anche fuori da Supabase.
create table users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  full_name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table divisions (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);
create index on divisions (org_id);

create table offices (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  division_id uuid not null references divisions(id) on delete restrict,
  name text not null,
  code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (division_id, name)
);
create index on offices (org_id);
create index on offices (division_id);

create table memberships (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner','admin','planner','member')),
  username text not null,
  division_id uuid references divisions(id) on delete set null,
  office_id uuid references offices(id) on delete set null,
  weekly_capacity_minutes integer check (weekly_capacity_minutes >= 0),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, user_id),
  unique (org_id, username)
);
create index on memberships (user_id);
create index on memberships (office_id);
create index on memberships (division_id);

create table skills (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);

create table membership_skills (
  membership_id uuid not null references memberships(id) on delete cascade,
  skill_id uuid not null references skills(id) on delete cascade,
  level smallint not null default 1 check (level between 1 and 5),
  primary key (membership_id, skill_id)
);
create index on membership_skills (skill_id);

-- ---------------------------------------------------------------- calendari
create table work_calendars (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  division_id uuid references divisions(id) on delete cascade,
  name text not null,
  -- minuti lavorativi per giorno ISO: 1 = lunedì ... 7 = domenica
  minutes_by_isodow integer[] not null default '{480,480,480,480,480,0,0}'
    check (array_length(minutes_by_isodow, 1) = 7),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on work_calendars (org_id);
create index on work_calendars (division_id);

create table calendar_exceptions (
  id uuid primary key default gen_random_uuid(),
  calendar_id uuid not null references work_calendars(id) on delete cascade,
  day date not null,
  minutes integer not null default 0 check (minutes >= 0),
  note text,
  unique (calendar_id, day)
);

-- ---------------------------------------------------------------- anagrafiche
create table customers (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);

create table project_types (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  code_prefix text not null check (code_prefix ~ '^[A-Z]{2,4}$'),  -- es. MAN, PG
  color text not null default '#6b7280' check (color ~ '^#[0-9a-fA-F]{6}$'),
  cover_path text,                                                -- file in storage
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name),
  unique (org_id, code_prefix)
);

create table activity_types (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  default_office_id uuid references offices(id) on delete set null,
  default_minutes integer check (default_minutes >= 0),
  is_indirect boolean not null default false,       -- lavoro indiretto d'ufficio
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);
create index on activity_types (default_office_id);

-- attività generate quando si crea una commessa di quel tipo
create table project_type_templates (
  id uuid primary key default gen_random_uuid(),
  project_type_id uuid not null references project_types(id) on delete cascade,
  activity_type_id uuid not null references activity_types(id) on delete restrict,
  phase_name text not null default 'Fase 1',
  sort_order integer not null default 0
);
create index on project_type_templates (project_type_id);
create index on project_type_templates (activity_type_id);

create table milestone_types (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);

create table delay_reasons (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, name)
);

-- ---------------------------------------------------------------- commesse
create table commesse (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  division_id uuid references divisions(id) on delete set null,
  project_type_id uuid not null references project_types(id) on delete restrict,
  customer_id uuid references customers(id) on delete restrict,   -- null = interna
  code text not null,                                             -- es. MAN26000037
  name text not null,
  subtitle text,
  status text not null default 'inserita'
    check (status in ('inserita','in_corso','in_attesa','chiusa','annullata')),
  portfolio text,
  quantity integer check (quantity >= 0),
  created_by uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, code)
);
create index on commesse (org_id, status);
create index on commesse (project_type_id);
create index on commesse (customer_id);
create index on commesse (division_id);

create table phases (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  commessa_id uuid not null references commesse(id) on delete cascade,
  seq integer not null check (seq > 0),                           -- -001
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (commessa_id, seq)
);
create index on phases (org_id);

create table milestones (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  commessa_id uuid not null references commesse(id) on delete cascade,
  phase_id uuid references phases(id) on delete cascade,
  milestone_type_id uuid references milestone_types(id) on delete set null,
  name text not null,
  due_week date not null check (extract(isodow from due_week) = 1),
  done_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on milestones (org_id, due_week);
create index on milestones (commessa_id);
create index on milestones (phase_id);
create index on milestones (milestone_type_id);

-- ---------------------------------------------------------------- attività
create table activities (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  phase_id uuid references phases(id) on delete cascade,          -- null = indiretta
  milestone_id uuid references milestones(id) on delete set null,
  activity_type_id uuid references activity_types(id) on delete set null,
  office_id uuid references offices(id) on delete set null,
  assignee_id uuid references memberships(id) on delete set null,
  predecessor_id uuid references activities(id) on delete set null,
  seq integer not null default 1 check (seq > 0),                 -- -01
  code text not null,                                             -- MAN26000037-001-01
  title text not null,
  description text,
  week_start date check (week_start is null or extract(isodow from week_start) = 1),
  status text not null default 'backlog'
    check (status in ('backlog','da_fare','in_corso','eseguito')),
  position double precision not null default 0,                   -- ordine nella colonna
  estimated_minutes integer not null default 0 check (estimated_minutes >= 0),
  is_indirect boolean not null default false,
  alert boolean not null default false,
  done_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, code),
  constraint no_self_predecessor check (predecessor_id is null or predecessor_id <> id),
  constraint done_has_date check ((status = 'eseguito') = (done_at is not null)),
  constraint planned_has_week check (status = 'backlog' or week_start is not null)
);
create index on activities (org_id, week_start, status, position);
create index on activities (assignee_id, week_start);
create index on activities (office_id, week_start);
create index on activities (phase_id);
create index on activities (milestone_id);
create index on activities (activity_type_id);
create index on activities (predecessor_id);

create table time_entries (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  activity_id uuid not null references activities(id) on delete cascade,
  membership_id uuid not null references memberships(id) on delete cascade,
  started_at timestamptz not null,
  ended_at timestamptz,                                           -- null = timer in corso
  minutes integer generated always as (
    case when ended_at is null then null
         else (extract(epoch from (ended_at - started_at)) / 60)::integer end
  ) stored,
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint positive_length check (ended_at is null or ended_at > started_at)
);
create index on time_entries (activity_id);
create index on time_entries (membership_id, started_at);
create index on time_entries (org_id, started_at);
-- un solo timer acceso per persona
create unique index one_running_timer on time_entries (membership_id) where ended_at is null;

create table activity_delays (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  activity_id uuid not null references activities(id) on delete cascade,
  delay_reason_id uuid not null references delay_reasons(id) on delete restrict,
  note text,
  reported_by uuid references memberships(id) on delete set null,
  created_at timestamptz not null default now()
);
create index on activity_delays (activity_id);
create index on activity_delays (delay_reason_id);
create index on activity_delays (reported_by);

create table import_logs (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  kind text not null check (kind in ('commesse','attivita','clienti','utenti')),
  file_path text not null,
  status text not null default 'in_corso' check (status in ('in_corso','ok','errori','fallito')),
  rows_total integer not null default 0,
  rows_ok integer not null default 0,
  errors jsonb not null default '[]',
  started_by uuid references memberships(id) on delete set null,
  started_at timestamptz not null default now(),
  finished_at timestamptz
);
create index on import_logs (org_id, started_at desc);

-- ---------------------------------------------------------------- viste
-- carico settimanale per persona: pianificato vs registrato
create view weekly_load with (security_invoker = true) as
select a.org_id,
       a.assignee_id as membership_id,
       a.week_start,
       sum(a.estimated_minutes)::integer as planned_minutes,
       coalesce(sum(t.logged), 0)::integer as logged_minutes
from activities a
left join lateral (
  select sum(te.minutes) as logged from time_entries te where te.activity_id = a.id
) t on true
where a.assignee_id is not null and a.week_start is not null
group by a.org_id, a.assignee_id, a.week_start;

-- ---------------------------------------------------------------- trigger
do $$
declare t text;
begin
  foreach t in array array['orgs','users','divisions','offices','memberships','skills',
    'work_calendars','customers','project_types','activity_types','milestone_types',
    'delay_reasons','commesse','phases','milestones','activities','time_entries']
  loop
    execute format('create trigger %I before update on %I for each row execute function set_updated_at()',
                   t || '_updated_at', t);
  end loop;
end $$;

-- ---------------------------------------------------------------- RLS
-- Su Supabase current_user_id() diventa auth.uid().
create or replace function current_user_id() returns uuid
language sql stable as $$ select nullif(current_setting('app.user_id', true), '')::uuid $$;

create or replace function is_member(p_org uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from memberships m
                 where m.org_id = p_org and m.user_id = current_user_id() and m.active)
$$;

create or replace function is_admin(p_org uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from memberships m
                 where m.org_id = p_org and m.user_id = current_user_id() and m.active
                   and m.role in ('owner','admin'))
$$;

do $$
declare t text;
begin
  -- dati operativi: ogni membro legge e scrive nella propria org
  foreach t in array array['commesse','phases','milestones','activities','time_entries',
    'activity_delays','customers','import_logs']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('create policy %I on %I for all using (is_member(org_id)) with check (is_member(org_id))',
                   t || '_member', t);
  end loop;
  -- impostazioni: tutti leggono, solo admin scrivono
  foreach t in array array['divisions','offices','memberships','skills','work_calendars',
    'project_types','activity_types','milestone_types','delay_reasons']
  loop
    execute format('alter table %I enable row level security', t);
    execute format('create policy %I on %I for select using (is_member(org_id))', t || '_read', t);
    execute format('create policy %I on %I for all using (is_admin(org_id)) with check (is_admin(org_id))',
                   t || '_admin', t);
  end loop;
end $$;

alter table orgs enable row level security;
create policy orgs_read on orgs for select using (is_member(id));
create policy orgs_admin on orgs for update using (is_admin(id)) with check (is_admin(id));

-- tabelle figlie senza org_id: accesso tramite il padre
alter table membership_skills enable row level security;
create policy membership_skills_read on membership_skills for select
  using (exists (select 1 from memberships m where m.id = membership_id and is_member(m.org_id)));
create policy membership_skills_admin on membership_skills for all
  using (exists (select 1 from memberships m where m.id = membership_id and is_admin(m.org_id)))
  with check (exists (select 1 from memberships m where m.id = membership_id and is_admin(m.org_id)));

alter table calendar_exceptions enable row level security;
create policy calendar_exceptions_read on calendar_exceptions for select
  using (exists (select 1 from work_calendars c where c.id = calendar_id and is_member(c.org_id)));
create policy calendar_exceptions_admin on calendar_exceptions for all
  using (exists (select 1 from work_calendars c where c.id = calendar_id and is_admin(c.org_id)))
  with check (exists (select 1 from work_calendars c where c.id = calendar_id and is_admin(c.org_id)));

alter table project_type_templates enable row level security;
create policy project_type_templates_read on project_type_templates for select
  using (exists (select 1 from project_types p where p.id = project_type_id and is_member(p.org_id)));
create policy project_type_templates_admin on project_type_templates for all
  using (exists (select 1 from project_types p where p.id = project_type_id and is_admin(p.org_id)))
  with check (exists (select 1 from project_types p where p.id = project_type_id and is_admin(p.org_id)));
