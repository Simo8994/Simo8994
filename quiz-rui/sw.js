// Conserva l'app e le domande per l'uso senza rete.
var VERSIONE = 'idoneo-v1';
var FILE = ['./', 'index.html', 'quesiti.json', 'icona.svg', 'icona-192.png', 'manifest.webmanifest'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSIONE).then(function (c) { return c.addAll(FILE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (nomi) {
    return Promise.all(nomi.filter(function (n) { return n !== VERSIONE; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});

// Prima la rete, così gli aggiornamenti arrivano subito; senza rete si usa la copia salvata.
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(function (r) {
      if (r.ok) { var copia = r.clone(); caches.open(VERSIONE).then(function (c) { c.put(e.request, copia); }); }
      return r;
    }).catch(function () {
      return caches.match(e.request, { ignoreSearch: true }).then(function (r) { return r || caches.match('index.html'); });
    })
  );
});
