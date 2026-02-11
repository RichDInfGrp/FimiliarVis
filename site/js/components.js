// Fimiliar Vis — Reusable UI components

export function renderPageHeader(container, title, caption = '') {
  const html = `
    <h1 class="page-title">${title}</h1>
    ${caption ? `<p class="page-caption">${caption}</p>` : ''}
    <hr class="divider">
  `;
  container.insertAdjacentHTML('beforeend', html);
}

export function renderKPIRow(container, metrics) {
  const cards = metrics
    .map(
      (m) => `
      <div class="kpi-card">
        <div class="kpi-label">${m.label}</div>
        <div class="kpi-value">${m.value}</div>
        ${m.delta ? `<div class="kpi-delta ${m.delta.startsWith('-') ? 'negative' : 'positive'}">${m.delta}</div>` : ''}
      </div>
    `
    )
    .join('');
  container.insertAdjacentHTML('beforeend', `<div class="kpi-row">${cards}</div>`);
}

export function renderComparisonCards(container, cards) {
  const html = cards
    .map((c) => {
      const delta = c.after - c.before;
      const pct = c.before ? ((delta / c.before) * 100).toFixed(0) : 0;
      const isPositive = delta >= 0;
      const fmt = (v) => typeof v === 'number' ? v.toLocaleString(undefined, { maximumFractionDigits: 0 }) : v;
      return `
        <div class="kpi-card">
          <div class="kpi-label">${c.label}</div>
          <div class="kpi-value">${fmt(c.after)}</div>
          <div class="kpi-delta ${isPositive ? 'positive' : 'negative'}">
            ${isPositive ? '+' : ''}${fmt(delta)} (${isPositive ? '+' : ''}${pct}%)
          </div>
          <div class="kpi-help">Before: ${fmt(c.before)}</div>
        </div>
      `;
    })
    .join('');
  container.insertAdjacentHTML('beforeend', `<div class="kpi-row">${html}</div>`);
}

export function renderChart(container, id) {
  container.insertAdjacentHTML('beforeend', `<div class="chart-card"><div id="${id}" class="chart-container"></div></div>`);
  return document.getElementById(id);
}

export function renderChartWithCaption(container, id, caption = '') {
  container.insertAdjacentHTML(
    'beforeend',
    `<div class="chart-card">
      <div id="${id}" class="chart-container"></div>
      ${caption ? `<p class="chart-caption">${caption}</p>` : ''}
    </div>`
  );
  return document.getElementById(id);
}

export function renderSectionTitle(container, title) {
  container.insertAdjacentHTML('beforeend', `<h2 class="section-title">${title}</h2>`);
}

export function renderGrid(container, cols = 2) {
  const grid = document.createElement('div');
  grid.className = `grid grid-${cols}`;
  container.appendChild(grid);
  return grid;
}

export function renderTable(container, data, columns, { linkColumns = [], maxRows = 50 } = {}) {
  if (!data || data.length === 0) {
    container.insertAdjacentHTML('beforeend', '<p class="text-secondary">No data available.</p>');
    return;
  }

  const rows = data.slice(0, maxRows);
  const headers = columns.map((c) => `<th>${c.label || c.key}</th>`).join('');
  const body = rows
    .map((row) => {
      const cells = columns
        .map((c) => {
          let val = row[c.key];
          if (val == null || val === 'NaT' || val === 'nan') val = '—';
          if (linkColumns.includes(c.key) && val !== '—') {
            val = `<a href="${val}" target="_blank" rel="noopener">View</a>`;
          } else if (typeof val === 'number') {
            val = c.format ? c.format(val) : val.toLocaleString();
          } else if (typeof val === 'string' && val.length > 60) {
            val = val.substring(0, 57) + '...';
          }
          return `<td>${val}</td>`;
        })
        .join('');
      return `<tr>${cells}</tr>`;
    })
    .join('');

  container.insertAdjacentHTML(
    'beforeend',
    `<div class="table-wrapper">
      <table class="data-table">
        <thead><tr>${headers}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>`
  );
}

export function renderSourceFooter(container, { source = '', updated = '', notes = '' } = {}) {
  const parts = [];
  if (source) parts.push(`<strong>Source:</strong> ${source}`);
  if (updated) parts.push(`<strong>Last updated:</strong> ${updated}`);
  if (notes) parts.push(`<strong>Notes:</strong> ${notes}`);

  container.insertAdjacentHTML(
    'beforeend',
    `<details class="source-footer">
      <summary>About this data</summary>
      <p>${parts.join(' &middot; ') || 'No metadata provided.'}</p>
    </details>`
  );
}

// Data fetching with cache
const dataCache = {};

export async function fetchData(filename) {
  if (dataCache[filename]) return dataCache[filename];
  const resp = await fetch(`data/${filename}`);
  if (!resp.ok) throw new Error(`Failed to load ${filename}`);
  const data = await resp.json();
  dataCache[filename] = data;
  return data;
}
