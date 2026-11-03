import path from 'node:path';
import fs from 'node:fs';
import express from 'express';
import { fileURLToPath } from 'node:url';
import { createApp } from './app.js';
import { createStore } from './store.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = process.env.DATA_DIR || path.join(root, 'data');
const port = Number(process.env.PORT || 3001);

let stripe = null;
if (process.env.STRIPE_SECRET_KEY) {
  if (!process.env.STRIPE_SECRET_KEY.startsWith('sk_test_')) {
    console.error('Il prototipo accetta solo chiavi Stripe di TEST (sk_test_...).');
    process.exit(1);
  }
  const { default: Stripe } = await import('stripe');
  stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
}

const adminToken = process.env.ADMIN_TOKEN || 'admin-dev';
if (!process.env.ADMIN_TOKEN) console.warn('ADMIN_TOKEN non impostato: uso "admin-dev" (solo sviluppo).');

const app = createApp({
  store: createStore(path.join(dataDir, 'db.json')),
  uploadDir: path.join(dataDir, 'uploads'),
  adminToken,
  stripe,
  baseUrl: process.env.BASE_URL || 'http://localhost:5173',
});

// In produzione serve anche il frontend compilato
const dist = path.join(root, 'dist');
if (fs.existsSync(dist)) {
  app.use(express.static(dist));
  app.get(/^(?!\/api).*/, (_req, res) => res.sendFile(path.join(dist, 'index.html')));
}

app.listen(port, () => {
  console.log(`API su http://localhost:${port} – pagamenti: ${stripe ? 'Stripe TEST' : 'simulati'}`);
});
