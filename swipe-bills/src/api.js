async function request(url, opts = {}) {
  const res = await fetch(url, opts);
  const body = res.headers.get('content-type')?.includes('json') ? await res.json() : null;
  if (!res.ok) throw new Error(body?.error || `Errore ${res.status}`);
  return body;
}

const json = (data) => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
const admin = (token, extra = {}) => ({ ...extra, headers: { ...(extra.headers || {}), 'x-admin-token': token } });

export const api = {
  config: () => request('/api/config'),
  bills: () => request('/api/bills'),
  upload: (formData) => request('/api/bills', { method: 'POST', body: formData }),
  pay: (id) => request(`/api/bills/${id}/pay`, { method: 'POST' }),
  release: (id) => request(`/api/bills/${id}/release`, { method: 'POST' }),
  confirm: (sessionId) => request('/api/checkout/confirm', json({ sessionId })),
  adminBills: (token) => request('/api/admin/bills', admin(token)),
  adminAction: (token, id, action) => request(`/api/admin/bills/${id}/${action}`, admin(token, { method: 'POST' })),
  adminDocument: async (token, url) => {
    const res = await fetch(url, admin(token));
    if (!res.ok) throw new Error('Documento non disponibile');
    return URL.createObjectURL(await res.blob());
  },
};

export const euro = (cents) => (cents / 100).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' });
