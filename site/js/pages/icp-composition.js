import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderGrid, renderTable, renderSourceFooter } from '../components.js';
import { horizontalBar } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [icpContacts, demographics] = await Promise.all([
    fetchData('contacts_icp.json'),
    fetchData('demographics.json'),
  ]);

  renderPageHeader(container, 'ICP Composition',
    'Who are the Ideal Customer Profile contacts? Breakdown by region, industry, company size, and comparison with LinkedIn audience demographics.');

  const countries = new Set(icpContacts.map((c) => c.country).filter(Boolean)).size;
  const industries = new Set(icpContacts.map((c) => c.industry).filter(Boolean)).size;
  const companies = new Set(icpContacts.map((c) => c.company).filter(Boolean)).size;

  renderKPIRow(container, [
    { label: 'ICP Contacts', value: String(icpContacts.length) },
    { label: 'Countries', value: String(countries) },
    { label: 'Industries', value: String(industries) },
    { label: 'Companies', value: String(companies) },
  ]);

  // Region + Industry side by side
  const grid = document.createElement('div');
  grid.className = 'grid grid-2';
  container.appendChild(grid);

  const leftCard = document.createElement('div');
  grid.appendChild(leftCard);
  renderSectionTitle(leftCard, 'ICP by Region');
  const regionCounts = countBy(icpContacts, 'country');
  const regionEl = renderChartWithCaption(leftCard, 'chart-region');
  horizontalBar(regionEl, regionCounts, { x: 'count', y: 'label', title: 'ICP Contacts by Country' });

  const rightCard = document.createElement('div');
  grid.appendChild(rightCard);
  renderSectionTitle(rightCard, 'ICP by Industry');
  const industryCounts = countBy(icpContacts, 'industry');
  const indEl = renderChartWithCaption(rightCard, 'chart-industry');
  horizontalBar(indEl, industryCounts, { x: 'count', y: 'label', title: 'ICP Contacts by Industry' });

  // Company size
  renderSectionTitle(container, 'ICP by Company Size');
  const sizeCounts = countBy(icpContacts, 'size');
  const sizeEl = renderChartWithCaption(container, 'chart-size');
  horizontalBar(sizeEl, sizeCounts, { x: 'count', y: 'label', title: 'ICP Contacts by Company Size' });

  // ICP contacts table
  renderSectionTitle(container, 'ICP Contacts Detail');
  renderTable(container, icpContacts, [
    { key: 'name', label: 'Name' },
    { key: 'title', label: 'Title' },
    { key: 'company', label: 'Company' },
    { key: 'country', label: 'Country' },
    { key: 'industry', label: 'Industry' },
    { key: 'size', label: 'Size' },
    { key: 'icp_tier', label: 'ICP Tier' },
    { key: 'profile_url', label: 'Profile' },
  ], { linkColumns: ['profile_url'] });

  // Demographics
  renderSectionTitle(container, 'LinkedIn Audience Demographics');
  container.insertAdjacentHTML('beforeend', '<p class="chart-caption" style="margin-bottom:0.75rem;">From Nicole\'s LinkedIn analytics — broader audience composition.</p>');

  const demoCategories = [...new Set(demographics.map((d) => d['Top Demographics']))];
  for (const cat of demoCategories) {
    const catData = demographics
      .filter((d) => d['Top Demographics'] === cat)
      .map((d) => ({ label: d.Value, count: Math.round(d.Percentage * 100 * 10) / 10 }))
      .sort((a, b) => b.count - a.count);

    const demoEl = renderChartWithCaption(container, `chart-demo-${cat.replace(/\s/g, '-')}`);
    horizontalBar(demoEl, catData, { x: 'count', y: 'label', title: `Audience by ${cat}`, textFormat: '.1f' });
  }

  renderSourceFooter(container, {
    source: 'Contacts enrichment + WorkSheet DEMOGRAPHICS',
    updated: '2026-02-09',
    notes: 'ICP = Broad | Global | Specific match. Demographics from LinkedIn audience analytics.',
  });
}

function countBy(arr, key) {
  const map = {};
  arr.forEach((item) => {
    const val = item[key];
    if (val) map[val] = (map[val] || 0) + 1;
  });
  return Object.entries(map)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count);
}
