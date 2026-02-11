import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderGrid, renderTable, renderSourceFooter } from '../components.js';
import { lineChart, horizontalBar } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [engagerSummary, weeklyIcp, reactions] = await Promise.all([
    fetchData('engager_summary.json'),
    fetchData('weekly_icp.json'),
    fetchData('enriched_reactions.json'),
  ]);

  const icpEngagers = engagerSummary.filter((e) => e.is_icp);
  const totalEngagers = engagerSummary.length;
  const totalIcpEngagements = icpEngagers.reduce((s, e) => s + e.total_engagements, 0);
  const icpCompanies = new Set(icpEngagers.map((e) => e.company).filter(Boolean)).size;

  renderPageHeader(container, 'Audience Quality',
    'Measuring the quality of engagement through ICP (Ideal Customer Profile) contacts.');

  renderKPIRow(container, [
    { label: 'Unique ICP Engagers', value: String(icpEngagers.length) },
    { label: 'Total ICP Engagements', value: totalIcpEngagements.toLocaleString() },
    { label: 'ICP % of Engagers', value: `${((icpEngagers.length / Math.max(totalEngagers, 1)) * 100).toFixed(1)}%` },
    { label: 'ICP Companies', value: String(icpCompanies) },
  ]);

  // ICP trend
  renderSectionTitle(container, 'ICP Engagement Over Time');
  if (weeklyIcp.length) {
    const trendEl = renderChartWithCaption(container, 'chart-icp-trend',
      'Weekly count of ICP engagements and unique ICP people engaging.');
    lineChart(trendEl, weeklyIcp, {
      x: 'week', y: ['icp_engagements', 'unique_icp_engagers'],
      title: 'Weekly ICP Engagements & Unique Engagers',
    });
  }

  // Reaction types
  renderSectionTitle(container, 'ICP Engagement by Reaction Type');
  if (reactions.length) {
    const reactEl = renderChartWithCaption(container, 'chart-reactions', 'What types of reactions ICP contacts are leaving.');
    horizontalBar(reactEl, reactions, { x: 'count', y: 'reactionType', title: 'ICP Engagements by Reaction Type' });
  }

  // Tables: top engagers + companies
  const grid = document.createElement('div');
  grid.className = 'grid grid-2';
  container.appendChild(grid);

  const leftCard = document.createElement('div');
  grid.appendChild(leftCard);
  renderSectionTitle(leftCard, 'Top ICP Engagers');
  renderTable(leftCard, icpEngagers.slice(0, 20), [
    { key: 'full_name', label: 'Name' },
    { key: 'title', label: 'Title' },
    { key: 'company', label: 'Company' },
    { key: 'total_engagements', label: 'Engagements' },
    { key: 'icp_tier', label: 'ICP Tier' },
  ]);

  const rightCard = document.createElement('div');
  grid.appendChild(rightCard);
  renderSectionTitle(rightCard, 'Top ICP Companies');
  const companyMap = {};
  icpEngagers.forEach((e) => {
    if (!e.company) return;
    if (!companyMap[e.company]) companyMap[e.company] = { company: e.company, total: 0, people: 0 };
    companyMap[e.company].total += e.total_engagements;
    companyMap[e.company].people++;
  });
  const companyData = Object.values(companyMap).sort((a, b) => b.total - a.total);
  renderTable(rightCard, companyData, [
    { key: 'company', label: 'Company' },
    { key: 'total', label: 'Total Engagements' },
    { key: 'people', label: 'People' },
  ]);

  renderSourceFooter(container, {
    source: 'Engagement data joined with Contacts enrichment',
    updated: '2026-02-09',
    notes: 'ICP = contacts matching Broad, Global, or Specific ICP criteria.',
  });
}
