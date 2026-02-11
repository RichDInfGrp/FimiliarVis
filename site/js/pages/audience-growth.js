import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderGrid, renderSourceFooter } from '../components.js';
import { lineChart, donutChart } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [kpis, followers, engDaily, engagerSummary] = await Promise.all([
    fetchData('kpis.json'),
    fetchData('followers.json'),
    fetchData('engagement_daily.json'),
    fetchData('engager_summary.json'),
  ]);

  renderPageHeader(container, 'Audience Growth',
    "Tracking follower growth, reach, and the composition of Nicole's engaged audience.");

  const icpEngagers = engagerSummary.filter((e) => e.is_icp).length;
  const totalEngagers = engagerSummary.length;

  renderKPIRow(container, [
    { label: 'Impressions', value: kpis.impressions_total.toLocaleString() },
    { label: 'Members Reached', value: kpis.members_reached.toLocaleString() },
    { label: 'Followers', value: kpis.latest_followers.toLocaleString(), delta: `+${kpis.new_followers}` },
    { label: 'Total Posts', value: String(kpis.total_posts) },
  ]);

  renderKPIRow(container, [
    { label: 'New Followers (24d)', value: `+${kpis.new_followers}` },
    { label: 'Unique Engagers', value: totalEngagers.toLocaleString() },
    { label: 'ICP Engagers', value: String(icpEngagers) },
    { label: 'ICP % of Engagers', value: `${((icpEngagers / Math.max(totalEngagers, 1)) * 100).toFixed(1)}%` },
  ]);

  // Followers trend
  renderSectionTitle(container, 'Follower Growth (24-Day Window)');
  const folEl = renderChartWithCaption(container, 'chart-followers',
    `Followers grew from ${kpis.start_followers.toLocaleString()} to ${kpis.latest_followers.toLocaleString()} (+${kpis.new_followers}).`);
  lineChart(folEl, followers, { x: 'Date', y: 'Total Followers', title: 'Total Followers Over Time' });

  // Grid: donut + daily
  const grid = document.createElement('div');
  grid.className = 'grid grid-2';
  container.appendChild(grid);

  // ICP donut
  const leftCard = document.createElement('div');
  grid.appendChild(leftCard);
  renderSectionTitle(leftCard, 'Engager Composition');
  const donutData = [
    { Category: 'ICP', Count: icpEngagers },
    { Category: 'Non-ICP', Count: totalEngagers - icpEngagers },
  ];
  const donutEl = renderChartWithCaption(leftCard, 'chart-donut',
    `${icpEngagers} of ${totalEngagers} unique engagers are ICP contacts.`);
  donutChart(donutEl, donutData, { values: 'Count', names: 'Category', title: 'ICP vs Non-ICP Engagers' });

  // Daily engagement
  const rightCard = document.createElement('div');
  grid.appendChild(rightCard);
  renderSectionTitle(rightCard, 'Daily Impressions & Engagements');
  const dailyEl = renderChartWithCaption(rightCard, 'chart-daily', 'Daily performance from the WorkSheet engagement data.');
  lineChart(dailyEl, engDaily, { x: 'Date', y: ['Impressions', 'Engagements'], title: 'Daily Impressions & Engagements' });

  renderSourceFooter(container, {
    source: 'WorkSheet (DISCOVERY, FOLLOWERS, ENGAGEMENT) + Engagement data',
    updated: '2026-02-09',
    notes: 'Follower data covers a 24-day window. ICP classification based on Fimiliar enrichment.',
  });
}
