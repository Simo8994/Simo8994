import React, { useState } from 'react';
import { api } from '../api.js';

export default function UploadForm({ categories }) {
  const [status, setStatus] = useState({ type: '', msg: '' });
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setStatus({ type: '', msg: '' });
    try {
      await api.upload(new FormData(e.target));
      e.target.reset();
      setStatus({ type: 'ok', msg: 'Bolletta inviata. Sarà visibile dopo la verifica del documento.' });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    } finally { setBusy(false); }
  };

  return (
    <form className="form" onSubmit={submit}>
      <label>Nome pubblico (facoltativo)<input name="nickname" maxLength={30} placeholder="es. Marco, Torino" /></label>
      <label>Email (privata, per aggiornamenti)<input name="email" type="email" required /></label>
      <label>Categoria
        <select name="category" required>{categories.map((c) => <option key={c}>{c}</option>)}</select>
      </label>
      <label>Fornitore da pagare<input name="payeeName" required placeholder="es. Enel Energia" /></label>
      <label>IBAN del fornitore (privato)<input name="payeeIban" required placeholder="IT60X0542811101000000123456" /></label>
      <div className="row">
        <label>Importo €<input name="amount" type="number" min="1" max="5000" step="0.01" required /></label>
        <label>Scadenza<input name="dueDate" type="date" required /></label>
      </div>
      <label>La tua storia (max 280)<textarea name="story" maxLength={280} rows={3} /></label>
      <label>Bolletta (PDF/JPG/PNG, max 5 MB)<input name="document" type="file" accept=".pdf,image/jpeg,image/png" required /></label>
      <p className="small">Il documento, l'IBAN e l'email non vengono mai mostrati pubblicamente: servono solo alla verifica.</p>
      <button className="primary" disabled={busy}>{busy ? 'Invio…' : 'Invia bolletta'}</button>
      {status.msg && <p className={status.type}>{status.msg}</p>}
    </form>
  );
}
