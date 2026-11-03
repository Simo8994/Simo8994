import React, { useEffect, useState } from 'react';
import SwipeDeck from './components/SwipeDeck.jsx';
import UploadForm from './components/UploadForm.jsx';
import AdminPanel from './components/AdminPanel.jsx';
import { api } from './api.js';

const TABS = [
  ['swipe', 'Paga bollette'],
  ['upload', 'Chiedi aiuto'],
  ['admin', 'Verifica'],
];

export default function App() {
  const [tab, setTab] = useState('swipe');
  const [config, setConfig] = useState(null);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    api.config().then(setConfig).catch(() => setNotice('API non raggiungibile'));

    // Ritorno da Stripe Checkout
    const params = new URLSearchParams(window.location.search);
    if (params.get('paid')) {
      api.confirm(params.get('paid'))
        .then((b) => setNotice(b.status === 'paid' ? 'Pagamento confermato. Grazie!' : 'Pagamento non completato.'))
        .catch((e) => setNotice(e.message));
    } else if (params.get('cancel')) {
      api.release(params.get('cancel')).catch(() => {});
      setNotice('Pagamento annullato.');
    }
    if (params.size) window.history.replaceState({}, '', '/');
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Swipe<span>Bills</span></h1>
        {config && <span className={`badge ${config.paymentMode}`}>Pagamenti: {config.paymentMode}</span>}
      </header>
      <nav>
        {TABS.map(([id, label]) => (
          <button key={id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}>{label}</button>
        ))}
      </nav>
      {notice && <p className="notice" onClick={() => setNotice('')}>{notice}</p>}
      <main>
        {tab === 'swipe' && <SwipeDeck />}
        {tab === 'upload' && config && <UploadForm categories={config.categories} />}
        {tab === 'admin' && <AdminPanel />}
      </main>
      <footer>Prototipo dimostrativo: nessun denaro reale viene trasferito.</footer>
    </div>
  );
}
