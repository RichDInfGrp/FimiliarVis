import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderSourceFooter } from '../components.js';
import { lineChart, scatterChart } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [weeklyPosts, weeklyIcp] = await Promise.all([
    fetchData('weekly_posts.json'),
    fetchData('weekly_icp.json'),
  ]);

  renderPageHeader(container, 'Acquisition Velocity',
    'How efficiently content acquires ICP engagement — ICP contacts per post and rolling trends.');

  // Merge weekly data
  const icpMap = {};
  weeklyIcp.forEach((w) => { icpMap[w.week] = w; });
  const weekly = weeklyPosts.map((w) => {
    const icp = icpMap[w.week] || { icp_engagements: 0, unique_icp_engagers: 0 };
    return { ...w, ...icp };
  });

  // Compute rolling averages
  weekly.forEach((w, i) => {
    w.icp_per_post = w.unique_icp_engagers / Math.max(w.num_posts, 1);
    const window = weekly.slice(Math.max(0, i - 3), i + 1);
    w.rolling_icp = window.reduce((s, d) => s + d.unique_icp_engagers, 0) / window.length;
    w.rolling_icp_per_post = window.reduce((s, d) => s + (d.icp_per_post || 0), 0) / window.length;
  });

  const totalIcp = weekly.reduce((s, w) => s + w.unique_icp_engagers, 0);
  const totalPosts = weekly.reduce((s, w) => s + w.num_posts, 0);

  renderKPIRow(container, [
    { label: 'Total ICP Engagers', value: String(totalIcp) },
    { label: 'Total Posts', value: String(totalPosts) },
    { label: 'ICP per Post (overall)', value: (totalIcp / Math.max(totalPosts, 1)).toFixed(2) },
    { label: 'Weeks of Data', value: String(weekly.length) },
  ]);

  // ICP per week + rolling
  renderSectionTitle(container, 'Weekly ICP Engagers & Rolling Average');
  const velEl = renderChartWithCaption(container, 'chart-velocity', 'Solid line shows 4-week rolling average of unique ICP engagers.');
  lineChart(velEl, weekly, { x: 'week', y: ['unique_icp_engagers', 'rolling_icp'], title: 'ICP Engagers per Week (with 4-week rolling avg)' });

  // ICP per post efficiency
  renderSectionTitle(container, 'ICP per Post Efficiency');
  const effEl = renderChartWithCaption(container, 'chart-efficiency', 'Efficiency metric: how many ICP contacts each post reaches.');
  lineChart(effEl, weekly, { x: 'week', y: ['icp_per_post', 'rolling_icp_per_post'], title: 'ICP Engagers per Post (with rolling avg)' });

  // Posts vs ICP scatter
  renderSectionTitle(container, 'Posts vs ICP Engagement');
  if (weekly.length > 2) {
    const scatEl = renderChartWithCaption(container, 'chart-scatter', 'Does posting more lead to more ICP engagement? Bubble size = total impressions.');
    scatterChart(scatEl, weekly, { x: 'num_posts', y: 'unique_icp_engagers', title: 'Weekly Posts vs ICP Engagers', size: 'total_impressions' });
  }

  // Scorecards
  renderSectionTitle(container, 'Efficiency Scorecards');
  const best = weekly.reduce((a, b) => (a.icp_per_post > b.icp_per_post ? a : b), weekly[0]);
  const most = weekly.reduce((a, b) => (a.unique_icp_engagers > b.unique_icp_engagers ? a : b), weekly[0]);
  const avgPosts = (weekly.reduce((s, w) => s + w.num_posts, 0) / weekly.length).toFixed(1);

  renderKPIRow(container, [
    { label: 'Best ICP/Post Week', value: best.icp_per_post.toFixed(2) },
    { label: 'Most ICP Engagers Week', value: String(most.unique_icp_engagers) },
    { label: 'Avg Posts/Week', value: avgPosts },
  ]);

  renderSourceFooter(container, {
    source: 'Daily Update + Engagement data (enriched)',
    updated: '2026-02-09',
    notes: 'ICP per post = unique ICP engagers / posts published that week.',
  });
}
