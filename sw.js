// investWEB service worker: proqramın özünü (səhifə, ikonlar) saxlayır ki,
// telefona quraşdırılsın və internet zəif olanda da açılsın.
// Bazar datası (CoinGecko, Finnhub və s.) heç vaxt keşlənmir — həmişə canlıdır.
const CACHE = "investweb-v8";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;   // API sorğularına toxunma
  // Əvvəl şəbəkə (həmişə ən son versiya), alınmasa keşdən
  e.respondWith(
    fetch(e.request)
      .then(res => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return res; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("./index.html")))
  );
});
