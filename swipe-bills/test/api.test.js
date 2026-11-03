import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createApp } from '../server/app.js';
import { createStore } from '../server/store.js';

const ADMIN = 'secret';
let server, base, tmp;

before(async () => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'swipebills-'));
  const app = createApp({ store: createStore(null), uploadDir: tmp, adminToken: ADMIN });
  server = app.listen(0);
  await new Promise((r) => server.once('listening', r));
  base = `http://localhost:${server.address().port}`;
});
after(() => { server.close(); fs.rmSync(tmp, { recursive: true, force: true }); });

function billForm(overrides = {}) {
  const fd = new FormData();
  const fields = {
    nickname: 'Marco', email: 'm@example.com', category: 'luce', payeeName: 'Enel Energia',
    payeeIban: 'IT60 X054 2811 1010 0000 0123 456', amount: '84,50', dueDate: '2026-12-01', story: 'Aiuto',
    ...overrides,
  };
  for (const [k, v] of Object.entries(fields)) fd.append(k, v);
  if (!('noFile' in overrides)) fd.append('document', new Blob(['%PDF-1.4'], { type: 'application/pdf' }), 'bolletta.pdf');
  return fd;
}

const post = (url, body, headers = {}) => fetch(base + url, { method: 'POST', body, headers });

test('flusso completo: carica → verifica → swipe a destra → pagata', async () => {
  let res = await post('/api/bills', billForm());
  assert.equal(res.status, 201);
  const bill = await res.json();
  assert.equal(bill.amountCents, 8450);
  assert.equal(bill.status, 'pending');
  assert.equal(bill.payeeIban, undefined, 'IBAN non deve essere pubblico');
  assert.equal(bill.email, undefined, 'email non deve essere pubblica');

  // Non ancora visibile ai benefattori
  assert.equal((await (await fetch(base + '/api/bills')).json()).length, 0);

  // Admin senza token → 401
  assert.equal((await post(`/api/admin/bills/${bill.id}/approve`)).status, 401);
  res = await post(`/api/admin/bills/${bill.id}/approve`, undefined, { 'x-admin-token': ADMIN });
  assert.equal(res.status, 200);

  const deck = await (await fetch(base + '/api/bills')).json();
  assert.equal(deck.length, 1);
  assert.equal(deck[0].documentFile, undefined);

  res = await post(`/api/bills/${bill.id}/pay`);
  const paid = await res.json();
  assert.equal(paid.mode, 'simulato');
  assert.equal(paid.bill.status, 'paid');

  // Doppio pagamento bloccato
  assert.equal((await post(`/api/bills/${bill.id}/pay`)).status, 409);
  assert.equal((await (await fetch(base + '/api/bills')).json()).length, 0);
});

test('validazione: IBAN errato, importo fuori range, file mancante', async () => {
  for (const o of [{ payeeIban: 'IT00X0000000000000000000000' }, { amount: '9000' }, { noFile: true }]) {
    const res = await post('/api/bills', billForm(o));
    assert.equal(res.status, 400, JSON.stringify(o));
  }
});

test('documento accessibile solo all\'admin', async () => {
  await post('/api/bills', billForm());
  const list = await (await fetch(base + '/api/admin/bills', { headers: { 'x-admin-token': ADMIN } })).json();
  const url = list.at(-1).documentUrl;
  assert.equal((await fetch(base + url)).status, 401);
  assert.equal((await fetch(base + url, { headers: { 'x-admin-token': ADMIN } })).status, 200);
});
