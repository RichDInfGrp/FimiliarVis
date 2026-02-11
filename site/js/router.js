// Fimiliar Vis — Hash-based SPA router

const pages = {};
let currentCleanup = null;

export function registerPage(hash, loadFn) {
  pages[hash] = loadFn;
}

export function navigate(hash) {
  window.location.hash = hash;
}

export async function initRouter() {
  const container = document.getElementById('main-content');

  async function route() {
    const hash = window.location.hash.slice(1) || 'home';

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach((link) => {
      link.classList.toggle('active', link.dataset.page === hash);
    });

    // Clean up previous page
    if (currentCleanup) {
      currentCleanup();
      currentCleanup = null;
    }

    container.innerHTML = '<div class="loading">Loading...</div>';

    const loadFn = pages[hash];
    if (loadFn) {
      try {
        const cleanup = await loadFn(container);
        if (typeof cleanup === 'function') currentCleanup = cleanup;
      } catch (err) {
        container.innerHTML = `<div class="error-message">Error loading page: ${err.message}</div>`;
        console.error(err);
      }
    } else {
      container.innerHTML = '<div class="error-message">Page not found.</div>';
    }

    // Scroll to top
    container.scrollTop = 0;
  }

  window.addEventListener('hashchange', route);

  // Nav link clicks
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigate(link.dataset.page);
    });
  });

  // Initial route
  route();
}
