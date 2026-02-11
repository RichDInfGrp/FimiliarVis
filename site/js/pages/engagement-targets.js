import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderTable, renderSourceFooter } from '../components.js';
import { lineChart } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [engagerSummary, weeklyIcp] = await Promise.all([
    fetchData('engager_summary.json'),
    fetchData('weekly_icp.json'),
  ]);

  renderPageHeader(container, 'Engagement Targets',
    'Actionable list of high-engagement contacts — hot leads for outreach.');

  const hotIcp = engagerSummary.filter((e) => e.total_engagements >= 5 && e.is_icp);
  const hotAll = engagerSummary.filter((e) => e.total_engagements >= 5);
  const icpOnly = engagerSummary.filter((e) => e.is_icp);

  renderKPIRow(container, [
    { label: 'ICP Hot Leads (5+)', value: String(hotIcp.length) },
    { label: 'All Hot Leads (5+)', value: String(hotAll.length) },
    { label: 'Total ICP Engagers', value: String(icpOnly.length) },
    { label: 'Avg Engagements (ICP)', value: icpOnly.length ? (icpOnly.reduce((s, e) => s + e.total_engagements, 0) / icpOnly.length).toFixed(1) : '0' },
  ]);

  // People table
  renderSectionTitle(container, 'Recommended People');
  const people = hotAll.sort((a, b) => b.total_engagements - a.total_engagements);
  renderTable(container, people.slice(0, 30), [
    { key: 'full_name', label: 'Name' },
    { key: 'title', label: 'Title' },
    { key: 'company', label: 'Company' },
    { key: 'country', label: 'Country' },
    { key: 'total_engagements', label: 'Engagements' },
    { key: 'likes', label: 'Likes' },
    { key: 'comments', label: 'Comments' },
    { key: 'unique_posts', label: 'Posts' },
    { key: 'last_engagement', label: 'Last Active' },
    { key: 'icp_tier', label: 'ICP Tier' },
  ]);

  // Companies
  renderSectionTitle(container, 'Top Companies by Engagement');
  const companyMap = {};
  hotAll.forEach((e) => {
    if (!e.company) return;
    if (!companyMap[e.company]) companyMap[e.company] = { company: e.company, total: 0, people: 0 };
    companyMap[e.company].total += e.total_engagements;
    companyMap[e.company].people++;
  });
  const companyData = Object.values(companyMap).sort((a, b) => b.total - a.total).slice(0, 15);
  renderTable(container, companyData, [
    { key: 'company', label: 'Company' },
    { key: 'total', label: 'Total Engagements' },
    { key: 'people', label: 'People' },
  ]);

  // ICP trend
  renderSectionTitle(container, 'ICP Engagement Trend');
  if (weeklyIcp.length) {
    const trendEl = renderChartWithCaption(container, 'chart-icp-trend', 'Number of unique ICP contacts engaging each week.');
    lineChart(trendEl, weeklyIcp, { x: 'week', y: 'unique_icp_engagers', title: 'Weekly Unique ICP Engagers' });
  }

  renderSourceFooter(container, {
    source: 'Engagement data enriched with Contacts',
    updated: '2026-02-09',
    notes: 'Hot leads = contacts with 5+ engagements.',
  });
}
