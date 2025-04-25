self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('dr-jingo-cache').then((cache) => {
            return cache.addAll([
                '/',
                '/chat',
                '/case_study',
                '/history',
                '/static/manifest.json',
                '/static/icons/icon-192.png',
                '/static/assets/img/bothead.png'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});