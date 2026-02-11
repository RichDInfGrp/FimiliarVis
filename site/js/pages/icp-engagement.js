import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderTable, renderSourceFooter } from '../components.js';
import { funnelChart, lineChart } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [kpis, engagerSummary, weeklyShare] = await Promise.all([
    fetchData('kpis.json'),
    fetchData('engager_summary.json'),
    fetchData('weekly_share.json'),
  ]);

  renderPageHeader(container, 'ICP Engagement',
    'Deep dive into how ICP contacts engage — from awareness to active participation.');

  const totalContacts = 189; // from contacts file
  const icpContacts = kpis.icp_contacts;
  const icpEngagers = engagerSummary.filter((e) => e.is_icp);
  const icpEngaged = icpEngagers.length;
  const icp3plus = icpEngagers.filter((e) => e.total_engagements >= 3).length;
  const icpCommented = icpEngagers.filter((e) => e.comments > 0).length;

  renderKPIRow(container, [
    { label: 'Total Contacts', value: String(totalContacts) },
    { label: 'ICP Contacts', value: String(icpContacts) },
    { label: 'ICP Engaged', value: String(icpEngaged) },
    { label: 'ICP 3+ Engagements', value: String(icp3plus) },
  ]);

  // Funnel
  renderSectionTitle(container, 'ICP Engagement Funnel');
  const funnelEl = renderChartWithCaption(container, 'chart-funnel',
    `From ${totalContacts} contacts → ${icpContacts} ICP → ${icpEngaged} engaged → ${icp3plus} with 3+ engagements → ${icpCommented} commented.`);
  funnelChart(funnelEl,
    ['All Contacts', 'ICP Contacts', 'ICP Engaged', '3+ Engagements', 'Commented'],
    [totalContacts, icpContacts, icpEngaged, icp3plus, icpCommented],
    { title: 'ICP Engagement Funnel' },
  );

  // ICP % over time
  renderSectionTitle(container, 'ICP Engagement Share Over Time');
  // Compute ICP % per week from weekly_share
  const weekMap = {};
  weeklyShare.forEach((w) => {
    if (!weekMap[w.week]) weekMap[w.week] = { week: w.week, total: 0, icp: 0 };
    weekMap[w.week].total += w.engagements;
    if (w.category === 'ICP') weekMap[w.week].icp += w.engagements;
  });
  const weeklyPct = Object.values(weekMap)
    .map((w) => ({ week: w.week, icp_pct: Math.round((w.icp / Math.max(w.total, 1)) * 1000) / 10 }))
    .sort((a, b) => a.week.localeCompare(b.week));

  if (weeklyPct.length) {
    const pctEl = renderChartWithCaption(container, 'chart-icp-pct', "Percentage of each week's engagements from ICP contacts.");
    lineChart(pctEl, weeklyPct, { x: 'week', y: 'icp_pct', title: 'ICP % of Weekly Engagements' });
  }

  // ICP engager details
  renderSectionTitle(container, 'ICP Engager Details');
  renderTable(container, icpEngagers, [
    { key: 'full_name', label: 'Name' },
    { key: 'title', label: 'Title' },
    { key: 'company', label: 'Company' },
    { key: 'country', label: 'Country' },
    { key: 'total_engagements', label: 'Engagements' },
    { key: 'likes', label: 'Likes' },
    { key: 'comments', label: 'Comments' },
    { key: 'unique_posts', label: 'Posts' },
    { key: 'first_engagement', label: 'First Seen' },
    { key: 'last_engagement', label: 'Last Active' },
    { key: 'icp_tier', label: 'ICP Tier' },
  ]);

  // Engaged but not in contacts
  renderSectionTitle(container, 'Engaged but Not in Contacts');
  container.insertAdjacentHTML('beforeend',
    '<p class="chart-caption" style="margin-bottom:0.75rem;">People who engaged with posts but aren\'t in the contacts database — potential new connections to pursue.</p>');

  const unknown = engagerSummary.filter((e) => e.icp_tier === 'Unknown').slice(0, 20);
  if (unknown.length) {
    renderTable(container, unknown, [
      { key: 'profile_url', label: 'Profile URL' },
      { key: 'total_engagements', label: 'Engagements' },
      { key: 'likes', label: 'Likes' },
      { key: 'comments', label: 'Comments' },
      { key: 'unique_posts', label: 'Posts' },
      { key: 'last_engagement', label: 'Last Active' },
    ], { linkColumns: ['profile_url'] });
  } else {
    container.insertAdjacentHTML('beforeend', '<p class="text-secondary">All engagers are in the contacts database.</p>');
  }

  renderSourceFooter(container, {
    source: 'Engagement + Contacts enrichment data',
    updated: '2026-02-09',
    notes: 'Funnel: All contacts → ICP match → engaged (any reaction) → 3+ engagements → commented.',
  });
}
