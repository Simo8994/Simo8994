"use client";
import { useActionState, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { login, type LoginState } from "./actions";
import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/Field";

export function LoginForm({ next }: { next: string }) {
  const [state, action, pending] = useActionState<LoginState, FormData>(login, { error: null, username: "" });
  const [username, setUsername] = useState(state.username);
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);

  return (
    <form action={action} className="grid gap-4" noValidate>
      <input type="hidden" name="next" value={next} />
      {state.error && <p role="alert" className="rounded-md bg-danger-soft px-3 py-2 text-sm text-danger">{state.error}</p>}
      <TextField label="Nome utente" name="username" autoComplete="username" autoCapitalize="none" spellCheck={false}
        value={username} onChange={(e) => setUsername(e.target.value)} required />
      <div className="relative">
        <TextField label="Password" name="password" type={show ? "text" : "password"} autoComplete="current-password"
          value={password} onChange={(e) => setPassword(e.target.value)} required className="[&_input]:pr-control-md" />
        <button type="button" onClick={() => setShow((v) => !v)} aria-label={show ? "Nascondi password" : "Mostra password"} aria-pressed={show}
          className="absolute bottom-0 right-0 grid h-control-md w-control-md place-items-center rounded-md text-text-muted hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
          {show ? <EyeOff aria-hidden className="h-icon w-icon" /> : <Eye aria-hidden className="h-icon w-icon" />}
        </button>
      </div>
      <a href="/login/recupero" className="w-max text-sm text-accent underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">Password dimenticata?</a>
      <Button type="submit" size="lg" loading={pending} disabled={!username || !password}>Entra</Button>
    </form>
  );
}
