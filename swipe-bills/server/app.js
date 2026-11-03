import express from 'express';
import multer from 'multer';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';

export const CATEGORIES = ['luce', 'gas', 'acqua', 'affitto', 'telefono', 'sanità', 'scuola', 'altro'];
const MAX_AMOUNT_CENTS = 500_000; // 5.000 €
const LOCK_MS = 30 * 60 * 1000; // una bolletta in checkout resta riservata 30 minuti
const ALLOWED_MIME = ['application/pdf', 'image/jpeg', 'image/png'];

// Solo i dati non personali escono dall'API pubblica:
// documento, IBAN e contatti restano visibili solo all'amministratore.
function publicView(b) {
  return {
    id: b.id,
    nickname: b.nickname,
    category: b.category,
    payeeName: b.payeeName,
    amountCents: b.amountCents,
    dueDate: b.dueDate,
    story: b.story,
    status: b.status,
  };
}

function isValidIban(raw) {
  const iban = String(raw || '').replace(/\s+/g, '').toUpperCase();
  if (!/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/.test(iban)) return false;
  // Controllo mod-97 (ISO 13616)
  const rearranged = iban.slice(4) + iban.slice(0, 4);
  const digits = rearranged.replace(/[A-Z]/g, (c) => String(c.charCodeAt(0) - 55));
  let rem = 0;
  for (const d of digits) rem = (rem * 10 + Number(d)) % 97;
  return rem === 1;
}

function isAvailable(b, now = Date.now()) {
  return b.status === 'open' && (!b.lockedUntil || b.lockedUntil < now);
}

export function createApp({ store, uploadDir, adminToken, stripe = null, baseUrl = 'http://localhost:5173' }) {
  const app = express();
  app.use(express.json());

  fs.mkdirSync(uploadDir, { recursive: true });
  const upload = multer({
    storage: multer.diskStorage({
      destination: uploadDir,
      filename: (_req, file, cb) => cb(null, crypto.randomUUID() + path.extname(file.originalname).toLowerCase()),
    }),
    limits: { fileSize: 5 * 1024 * 1024 },
    fileFilter: (_req, file, cb) => cb(null, ALLOWED_MIME.includes(file.mimetype)),
  });

  const requireAdmin = (req, res, next) => {
    if (!adminToken || req.get('x-admin-token') !== adminToken) {
      return res.status(401).json({ error: 'Non autorizzato' });
    }
    next();
  };

  app.get('/api/config', (_req, res) => {
    res.json({ categories: CATEGORIES, paymentMode: stripe ? 'stripe-test' : 'simulato' });
  });

  // --- Richiedente: carica una bolletta ---
  app.post('/api/bills', (req, res) => {
    upload.single('document')(req, res, (err) => {
      if (err) return res.status(400).json({ error: err.code === 'LIMIT_FILE_SIZE' ? 'File troppo grande (max 5 MB)' : 'Upload non valido' });

      const { nickname, category, payeeName, payeeIban, amount, dueDate, story, email } = req.body;
      const amountCents = Math.round(Number(String(amount).replace(',', '.')) * 100);
      const errors = [];
      if (!req.file) errors.push('Documento mancante (PDF, JPG o PNG)');
      if (!CATEGORIES.includes(category)) errors.push('Categoria non valida');
      if (!payeeName || payeeName.trim().length < 2) errors.push('Fornitore mancante');
      if (!isValidIban(payeeIban)) errors.push('IBAN del fornitore non valido');
      if (!Number.isFinite(amountCents) || amountCents < 100 || amountCents > MAX_AMOUNT_CENTS) errors.push('Importo tra 1 € e 5.000 €');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(dueDate || '')) errors.push('Scadenza non valida');
      if (!email || !/^\S+@\S+\.\S+$/.test(email)) errors.push('Email non valida');

      if (errors.length) {
        if (req.file) fs.rmSync(req.file.path, { force: true });
        return res.status(400).json({ error: errors.join('; ') });
      }

      const bill = store.create({
        nickname: (nickname || 'Anonimo').trim().slice(0, 30),
        category,
        payeeName: payeeName.trim().slice(0, 80),
        payeeIban: payeeIban.replace(/\s+/g, '').toUpperCase(),
        amountCents,
        dueDate,
        story: (story || '').trim().slice(0, 280),
        email: email.trim(),
        documentFile: req.file.filename,
      });
      res.status(201).json(publicView(bill));
    });
  });

  // --- Benefattore: mazzo di bollette verificate ---
  app.get('/api/bills', (_req, res) => {
    const now = Date.now();
    const bills = store
      .list((b) => isAvailable(b, now))
      .sort((a, b) => a.dueDate.localeCompare(b.dueDate))
      .map(publicView);
    res.json(bills);
  });

  // Swipe a destra: avvia il pagamento
  app.post('/api/bills/:id/pay', async (req, res) => {
    const bill = store.get(req.params.id);
    if (!bill) return res.status(404).json({ error: 'Bolletta non trovata' });
    if (!isAvailable(bill)) return res.status(409).json({ error: 'Bolletta già pagata o in pagamento' });

    if (!stripe) {
      // Modalità simulata: nessun denaro reale.
      store.update(bill.id, { status: 'paid', paidAt: new Date().toISOString(), paymentRef: 'SIMULATO' });
      return res.json({ mode: 'simulato', bill: publicView(store.get(bill.id)) });
    }

    store.update(bill.id, { lockedUntil: Date.now() + LOCK_MS });
    try {
      const session = await stripe.checkout.sessions.create({
        mode: 'payment',
        line_items: [{
          quantity: 1,
          price_data: {
            currency: 'eur',
            unit_amount: bill.amountCents,
            product_data: { name: `Bolletta ${bill.category} – ${bill.payeeName}` },
          },
        }],
        metadata: { billId: bill.id },
        success_url: `${baseUrl}/?paid={CHECKOUT_SESSION_ID}`,
        cancel_url: `${baseUrl}/?cancel=${bill.id}`,
        expires_at: Math.floor((Date.now() + LOCK_MS) / 1000),
      });
      store.update(bill.id, { checkoutSessionId: session.id });
      res.json({ mode: 'stripe-test', url: session.url });
    } catch (e) {
      store.update(bill.id, { lockedUntil: null });
      res.status(502).json({ error: 'Errore Stripe: ' + e.message });
    }
  });

  // Ritorno da Stripe Checkout: verifica lato server che il pagamento sia avvenuto
  app.post('/api/checkout/confirm', async (req, res) => {
    if (!stripe) return res.status(400).json({ error: 'Stripe non configurato' });
    try {
      const session = await stripe.checkout.sessions.retrieve(String(req.body.sessionId || ''));
      const bill = store.get(session.metadata?.billId);
      if (!bill) return res.status(404).json({ error: 'Bolletta non trovata' });
      if (session.payment_status === 'paid' && bill.status !== 'paid') {
        store.update(bill.id, { status: 'paid', paidAt: new Date().toISOString(), paymentRef: session.payment_intent, lockedUntil: null });
      }
      res.json(publicView(store.get(bill.id)));
    } catch (e) {
      res.status(400).json({ error: 'Sessione non valida' });
    }
  });

  app.post('/api/bills/:id/release', (req, res) => {
    const bill = store.get(req.params.id);
    if (bill && bill.status === 'open') store.update(bill.id, { lockedUntil: null });
    res.json({ ok: true });
  });

  // --- Amministratore: verifica documenti ---
  app.get('/api/admin/bills', requireAdmin, (_req, res) => {
    res.json(store.list().map(({ documentFile, ...rest }) => ({ ...rest, documentUrl: `/api/admin/document/${documentFile}` })));
  });

  app.get('/api/admin/document/:file', requireAdmin, (req, res) => {
    const file = path.basename(req.params.file);
    res.sendFile(path.resolve(uploadDir, file), (err) => err && res.status(404).end());
  });

  app.post('/api/admin/bills/:id/:action(approve|reject|payout)', requireAdmin, (req, res) => {
    const bill = store.get(req.params.id);
    if (!bill) return res.status(404).json({ error: 'Bolletta non trovata' });
    const { action } = req.params;
    if (action === 'approve' && bill.status === 'pending') store.update(bill.id, { status: 'open' });
    else if (action === 'reject' && bill.status === 'pending') store.update(bill.id, { status: 'rejected' });
    else if (action === 'payout' && bill.status === 'paid') store.update(bill.id, { payoutAt: new Date().toISOString() });
    else return res.status(409).json({ error: `Azione "${action}" non valida per stato "${bill.status}"` });
    res.json(store.get(bill.id));
  });

  return app;
}
