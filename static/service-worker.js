self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('osler-v1').then(cache => {
      return cache.addAll(['/', '/static/css/styles.css', '/static/js/main.js']);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});