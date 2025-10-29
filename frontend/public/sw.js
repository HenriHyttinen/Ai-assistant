// Service Worker for Numbers Don't Lie Health App
// Provides offline functionality and caching

const CACHE_NAME = 'numbers-dont-lie-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';
const API_CACHE = 'api-v1';

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  // Add other static assets as needed
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/recipes',
  '/meal-plans',
  '/nutrition/preferences',
  '/nutrition/goals',
  '/micronutrients/goals',
  '/achievements',
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Static files cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Error caching static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle different types of requests
  if (request.method === 'GET') {
    // Static files
    if (url.pathname.startsWith('/static/') || 
        url.pathname.endsWith('.js') || 
        url.pathname.endsWith('.css') ||
        url.pathname.endsWith('.png') ||
        url.pathname.endsWith('.jpg') ||
        url.pathname.endsWith('.svg')) {
      event.respondWith(handleStaticRequest(request));
    }
    // API requests
    else if (url.pathname.startsWith('/api/') || 
             API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint))) {
      event.respondWith(handleApiRequest(request));
    }
    // HTML pages
    else if (request.headers.get('accept')?.includes('text/html')) {
      event.respondWith(handlePageRequest(request));
    }
    // Other requests
    else {
      event.respondWith(handleOtherRequest(request));
    }
  }
});

// Handle static file requests
async function handleStaticRequest(request) {
  try {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Error handling static request:', error);
    return new Response('Offline - Static file not available', { status: 503 });
  }
}

// Handle API requests
async function handleApiRequest(request) {
  try {
    const cache = await caches.open(API_CACHE);
    const cachedResponse = await cache.match(request);
    
    // Try network first for API requests
    try {
      const networkResponse = await fetch(request);
      if (networkResponse.ok) {
        // Cache successful responses
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    } catch (networkError) {
      // Network failed, try cache
      if (cachedResponse) {
        console.log('Serving API from cache:', request.url);
        return cachedResponse;
      }
      
      // No cache available, return offline response
      return new Response(
        JSON.stringify({ 
          error: 'Offline', 
          message: 'This data is not available offline',
          offline: true 
        }),
        { 
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
  } catch (error) {
    console.error('Error handling API request:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'Service unavailable',
        offline: true 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle page requests
async function handlePageRequest(request) {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Error handling page request:', error);
    // Return offline page
    return new Response(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Offline - Numbers Don't Lie</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { 
              font-family: system-ui, sans-serif; 
              text-align: center; 
              padding: 50px; 
              background: #f5f5f5;
            }
            .offline-container {
              max-width: 400px;
              margin: 0 auto;
              background: white;
              padding: 40px;
              border-radius: 8px;
              box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .offline-icon {
              font-size: 48px;
              margin-bottom: 20px;
            }
            h1 { color: #333; margin-bottom: 16px; }
            p { color: #666; margin-bottom: 24px; }
            button {
              background: #3182ce;
              color: white;
              border: none;
              padding: 12px 24px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 16px;
            }
            button:hover { background: #2c5aa0; }
          </style>
        </head>
        <body>
          <div class="offline-container">
            <div class="offline-icon">📱</div>
            <h1>You're Offline</h1>
            <p>Don't worry! You can still view your saved recipes and meal plans.</p>
            <button onclick="window.location.reload()">Try Again</button>
          </div>
        </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Handle other requests
async function handleOtherRequest(request) {
  try {
    return await fetch(request);
  } catch (error) {
    console.error('Error handling other request:', error);
    return new Response('Offline', { status: 503 });
  }
}

// Background sync for when connection is restored
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-recipes') {
    event.waitUntil(syncRecipes());
  } else if (event.tag === 'sync-meal-plans') {
    event.waitUntil(syncMealPlans());
  }
});

// Sync recipes when online
async function syncRecipes() {
  try {
    console.log('Syncing recipes...');
    // Implementation would sync local changes with server
    // This is a placeholder for the actual sync logic
  } catch (error) {
    console.error('Error syncing recipes:', error);
  }
}

// Sync meal plans when online
async function syncMealPlans() {
  try {
    console.log('Syncing meal plans...');
    // Implementation would sync local changes with server
    // This is a placeholder for the actual sync logic
  } catch (error) {
    console.error('Error syncing meal plans:', error);
  }
}

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'CACHE_RECIPES':
      cacheRecipes(data);
      break;
    case 'CACHE_MEAL_PLANS':
      cacheMealPlans(data);
      break;
    case 'CLEAR_CACHE':
      clearCache();
      break;
    default:
      console.log('Unknown message type:', type);
  }
});

// Cache recipes for offline access
async function cacheRecipes(recipes) {
  try {
    const cache = await caches.open(API_CACHE);
    const response = new Response(JSON.stringify(recipes), {
      headers: { 'Content-Type': 'application/json' }
    });
    await cache.put('/api/recipes', response);
    console.log('Recipes cached for offline access');
  } catch (error) {
    console.error('Error caching recipes:', error);
  }
}

// Cache meal plans for offline access
async function cacheMealPlans(mealPlans) {
  try {
    const cache = await caches.open(API_CACHE);
    const response = new Response(JSON.stringify(mealPlans), {
      headers: { 'Content-Type': 'application/json' }
    });
    await cache.put('/api/meal-plans', response);
    console.log('Meal plans cached for offline access');
  } catch (error) {
    console.error('Error caching meal plans:', error);
  }
}

// Clear cache
async function clearCache() {
  try {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('All caches cleared');
  } catch (error) {
    console.error('Error clearing cache:', error);
  }
}


