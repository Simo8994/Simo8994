import React, { useState } from 'react';
import { api, euro } from '../api.js';

const LABEL = { pending: 'Da verificare', open: 'Pubblicata', paid: 'Pagata', rejected: 'Rifiutata' };

export default function AdminPanel() {
  const [token, setToken] = useState(() => { try { return sessionStorage.getItem('adminToken') || ''; } catch { return ''; } });
  const [bills, setBills] = useState(null);
  const [error, setError] = useState('');

  const load = async (t = token) => {
    setError('');
    try {
      setBills(await api.adminBills(t));
      try { sessionStorage.setItem('adminToken', t); } catch { /* ignora */ }
    } catch (e) { setError(e.message); setBills(null); }
  };

  const act = async (id, action) => {
    try { await api.adminAction(token, id, action); load(); } catch (e) { setError(e.message); }
  };

  const openDoc = async (url) => {
    try { window.open(await api.adminDocument(token, url), '_blank'); } catch (e) { setError(e.message); }
  };

  return (
    <section className="admin">
      <form className="row" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <input type="password" placeholder="Token amministratore" value={token} onChange={(e) => setToken(e.target.value)} />
        <button className="primary">Accedi</button>
      </form>
      {error && <p className="error">{error}</p>}
      {bills && bills.length === 0 && <p>Nessuna bolletta.</p>}
      {bills?.map((b) => (
        <div key={b.id} className={`admin-item ${b.status}`}>
          <div>
            <b>{euro(b.amountCents)}</b> · {b.category} · {b.payeeName} · scad. {b.dueDate}
            <div className="small">{b.nickname} &lt;{b.email}&gt; · IBAN {b.payeeIban}</div>
            <div className="small">Stato: {LABEL[b.status]}{b.paymentRef ? ` · rif. ${b.paymentRef}` : ''}{b.payoutAt ? ' · girata al fornitore' : ''}</div>
          </div>
          <div className="row">
            <button onClick={() => openDoc(b.documentUrl)}>Documento</button>
            {b.status === 'pending' && <>
              <button className="primary" onClick={() => act(b.id, 'approve')}>Approva</button>
              <button onClick={() => act(b.id, 'reject')}>Rifiuta</button>
            </>}
            {b.status === 'paid' && !b.payoutAt && <button className="primary" onClick={() => act(b.id, 'payout')}>Segna girata</button>}
          </div>
        </div>
      ))}
    </section>
  );
}
