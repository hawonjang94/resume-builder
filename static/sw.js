const CACHE_NAME = "resume-builder-v1";
const STATIC_ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/app.js",
  "/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

// 1. 서비스 워커 설치 시 정적 자산 캐싱
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// 2. 새로운 서비스 워커 활성화 시 구버전 캐시 정리
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// 3. 네트워크 요청 가로채기 (POST/API 요청은 캐시하지 않음)
self.addEventListener("fetch", (event) => {
  // POST 요청 등 비-GET 요청은 항상 네트워크로 전달
  if (event.request.method !== "GET") {
    return;
  }

  // CDN 라이브러리 및 정적 자산 캐싱 전략 (Network first with cache fallback)
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 유효한 응답인 경우 캐시 업데이트
        if (response && response.status === 200 && response.type === "basic") {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // 오프라인 상태일 때 캐시된 응답 반환
        return caches.match(event.request);
      })
  );
});
