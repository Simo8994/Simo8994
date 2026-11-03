import React, { useEffect, useRef, useState } from 'react';
import { api, euro } from '../api.js';

const SKIP_KEY = 'swipebills:skipped';
const THRESHOLD = 110;

function loadSkipped() {
  try { return new Set(JSON.parse(localStorage.getItem(SKIP_KEY) || '[]')); } catch { return new Set(); }
}
function saveSkipped(set) {
  try { localStorage.setItem(SKIP_KEY, JSON.stringify([...set])); } catch { /* ignora */ }
}

function daysLeft(date) {
  const d = Math.ceil((new Date(date) - new Date()) / 86_400_000);
  return d < 0 ? 'scaduta' : d === 0 ? 'scade oggi' : `scade tra ${d} gg`;
}

export default function SwipeDeck() {
  const [bills, setBills] = useState(null);
  const [error, setError] = useState('');
  const [drag, setDrag] = useState({ x: 0, active: false });
  const [confirming, setConfirming] = useState(null);
  const [busy, setBusy] = useState(false);
  const start = useRef(0);

  const load = () => {
    const skipped = loadSkipped();
    api.bills().then((all) => setBills(all.filter((b) => !skipped.has(b.id)))).catch((e) => setError(e.message));
  };
  useEffect(load, []);

  const top = bills?.[0];

  const removeTop = () => { setBills((b) => b.slice(1)); setDrag({ x: 0, active: false }); };

  const skip = () => {
    const s = loadSkipped(); s.add(top.id); saveSkipped(s);
    removeTop();
  };

  const pay = async () => {
    setBusy(true); setError('');
    try {
      const res = await api.pay(confirming.id);
      if (res.url) { window.location.href = res.url; return; } // Stripe Checkout
      setConfirming(null);
      removeTop();
    } catch (e) {
      setError(e.message); setConfirming(null); load();
    } finally { setBusy(false); }
  };

  const onDown = (e) => { start.current = e.clientX; setDrag({ x: 0, active: true }); e.currentTarget.setPointerCapture(e.pointerId); };
  const onMove = (e) => drag.active && setDrag({ x: e.clientX - start.current, active: true });
  const onUp = () => {
    if (drag.x > THRESHOLD) { setDrag({ x: 0, active: false }); setConfirming(top); }
    else if (drag.x < -THRESHOLD) skip();
    else setDrag({ x: 0, active: false });
  };

  if (error && !bills) return <p className="error">{error}</p>;
  if (!bills) return <p>Caricamento…</p>;

  return (
    <section className="deck">
      {error && <p className="error">{error}</p>}
      {!top ? (
        <div className="empty">
          <p>Nessuna bolletta da mostrare.</p>
          <button onClick={() => { saveSkipped(new Set()); load(); }}>Ricarica (anche le scartate)</button>
        </div>
      ) : (
        <>
          <div className="stack">
            {bills.slice(0, 3).reverse().map((b) => {
              const isTop = b.id === top.id;
              const style = isTop ? { transform: `translateX(${drag.x}px) rotate(${drag.x / 15}deg)`, transition: drag.active ? 'none' : 'transform .25s' } : undefined;
              return (
                <article key={b.id} className={`card ${isTop ? 'top' : ''}`} style={style}
                  {...(isTop && { onPointerDown: onDown, onPointerMove: onMove, onPointerUp: onUp, onPointerCancel: onUp })}>
                  {isTop && drag.x > 30 && <span className="stamp pay">PAGO</span>}
                  {isTop && drag.x < -30 && <span className="stamp skip">PASSO</span>}
                  <div className="cat">{b.category}</div>
                  <div className="amount">{euro(b.amountCents)}</div>
                  <div className="payee">a {b.payeeName}</div>
                  <div className="due">{daysLeft(b.dueDate)} · {new Date(b.dueDate).toLocaleDateString('it-IT')}</div>
                  {b.story && <p className="story">“{b.story}”</p>}
                  <div className="who">— {b.nickname}</div>
                </article>
              );
            })}
          </div>
          <div className="actions">
            <button className="skip" onClick={skip} aria-label="Passa">✕</button>
            <button className="pay" onClick={() => setConfirming(top)} aria-label="Paga">♥</button>
          </div>
          <p className="hint">Trascina a destra per pagare, a sinistra per passare.</p>
        </>
      )}

      {confirming && (
        <div className="modal" role="dialog">
          <div className="modal-box">
            <h3>Confermi il pagamento?</h3>
            <p>Paghi <b>{euro(confirming.amountCents)}</b> della bolletta {confirming.category} di {confirming.nickname}.</p>
            <p className="small">L'importo viene girato direttamente al fornitore ({confirming.payeeName}), non al richiedente.</p>
            <div className="row">
              <button onClick={() => setConfirming(null)} disabled={busy}>Annulla</button>
              <button className="primary" onClick={pay} disabled={busy}>{busy ? 'Attendi…' : 'Paga'}</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
