const CACHE_NAME = 'cabril-cache-v1';
const urlsToCache = [
    '/',
    // ADICIONAR CSS PARA FICAR EM CACHE
    '/static/css/adicionar_utilizador.css',
    '/static/css/alterar_password.css',
    '/static/css/base.css',
    '/static/css/calendario.css',
    '/static/css/criar_conta.css',
    '/static/css/criar_evento.css',
    '/static/css/definicoes.css',
    '/static/css/gestao_carrinha.css',
    '/static/css/login.css',
    '/static/css/membros.css',
    '/static/css/reservas_detalhes.css',
    '/static/css/ver_registos.css',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Retorna do cache ou busca da rede
        return response || fetch(event.request);
      })
  );
});
