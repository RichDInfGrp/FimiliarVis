// Fimiliar Vis — Simple client-side authentication

import { CREDENTIALS } from './config.js';

const AUTH_KEY = 'fimiliar_auth';

export function isAuthenticated() {
  return sessionStorage.getItem(AUTH_KEY) === 'true';
}

export function login(username, password) {
  if (username === CREDENTIALS.username && password === CREDENTIALS.password) {
    sessionStorage.setItem(AUTH_KEY, 'true');
    return true;
  }
  return false;
}

export function logout() {
  sessionStorage.removeItem(AUTH_KEY);
  window.location.reload();
}

export function initAuth() {
  const overlay = document.getElementById('login-overlay');
  const app = document.getElementById('app');
  const form = document.getElementById('login-form');
  const error = document.getElementById('login-error');

  if (isAuthenticated()) {
    overlay.style.display = 'none';
    app.style.display = 'flex';
    return;
  }

  overlay.style.display = 'flex';
  app.style.display = 'none';

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (login(username, password)) {
      overlay.style.display = 'none';
      app.style.display = 'flex';
      window.dispatchEvent(new Event('hashchange'));
    } else {
      error.textContent = 'Invalid username or password.';
      error.style.display = 'block';
    }
  });
}
