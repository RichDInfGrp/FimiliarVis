import { fetchData, renderPageHeader, renderKPIRow, renderComparisonCards, renderChartWithCaption, renderSectionTitle, renderTable, renderSourceFooter, renderGrid } from '../components.js';
import { comboChart, horizontalBar } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [kpis, posts, weeklyPosts, topPosts] = await Promise.all([
    fetchData('kpis.json'),
    fetchData('posts.json'),
    fetchData('weekly_posts.json'),
    fetchData('top_posts.json'),
  ]);

  renderPageHeader(container, 'Content Performance',
    "How Nicole's LinkedIn content performs week-over-week, and the impact since Fimiliar's service began.");

  renderKPIRow(container, [
    { label: 'Total Posts', value: String(kpis.total_posts) },
    { label: 'Avg Impressions / Post', value: Math.round(kpis.avg_impressions).toLocaleString() },
    { label: 'Avg Engagements / Post', value: Math.round(kpis.avg_engagements_per_post).toLocaleString() },
    { label: 'Avg Engagement Rate', value: `${kpis.avg_engagement_rate}%` },
  ]);

  // Weekly combo chart
  renderSectionTitle(container, 'Weekly Performance');
  const comboEl = renderChartWithCaption(container, 'chart-weekly-combo',
    'Bars show total weekly volume; line shows average engagement rate per post.');
  comboChart(comboEl, weeklyPosts, {
    x: 'week',
    barY: ['total_impressions', 'total_engagements'],
    lineY: ['avg_rate'],
    barNames: ['Impressions', 'Engagements'],
    lineNames: ['Avg Rate (%)'],
    title: 'Weekly Impressions, Engagements & Rate',
  });

  // Before/After comparison
  renderSectionTitle(container, 'Before vs After Fimiliar');
  const before = topPosts.filter((p) => p.period === 'Before');
  const after = topPosts.filter((p) => p.period === 'After');

  if (before.length && after.length) {
    const avg = (arr, key) => arr.reduce((s, d) => s + (d[key] || 0), 0) / arr.length;
    renderComparisonCards(container, [
      { label: 'Avg Impressions / Post', before: avg(before, 'impressions'), after: avg(after, 'impressions') },
      { label: 'Top Post Impressions', before: Math.max(...before.map((d) => d.impressions)), after: Math.max(...after.map((d) => d.impressions)) },
      { label: 'Posts Tracked', before: before.length, after: after.length },
      { label: 'Total Impressions', before: before.reduce((s, d) => s + d.impressions, 0), after: after.reduce((s, d) => s + d.impressions, 0) },
    ]);
  }

  // Format breakdown
  renderSectionTitle(container, 'Performance by Post Format');
  const formatMap = {};
  posts.forEach((p) => {
    if (!formatMap[p.post_format]) formatMap[p.post_format] = { count: 0, imp: 0, eng: 0 };
    formatMap[p.post_format].count++;
    formatMap[p.post_format].imp += p.impressions;
    formatMap[p.post_format].eng += p.engagements;
  });
  const formatData = Object.entries(formatMap)
    .map(([fmt, v]) => ({ post_format: fmt, avg_impressions: Math.round(v.imp / v.count) }))
    .sort((a, b) => b.avg_impressions - a.avg_impressions);

  const formatEl = renderChartWithCaption(container, 'chart-format', 'Which content formats drive the most visibility.');
  horizontalBar(formatEl, formatData, { x: 'avg_impressions', y: 'post_format', title: 'Average Impressions by Post Format' });

  // Top posts table
  renderSectionTitle(container, 'Top Posts');
  const topByImp = [...posts].sort((a, b) => b.impressions - a.impressions).slice(0, 10);
  renderTable(container, topByImp, [
    { key: 'posted_at', label: 'Date' },
    { key: 'post_format', label: 'Format' },
    { key: 'impressions', label: 'Impressions' },
    { key: 'engagements', label: 'Engagements' },
    { key: 'engagement_rate', label: 'Rate (%)' },
    { key: 'post_url', label: 'Link' },
  ], { linkColumns: ['post_url'] });

  renderSourceFooter(container, {
    source: "Nicole's Daily Update + WorkSheet TOP POSTS",
    updated: '2026-02-09',
    notes: 'Before period: Dec 2024 – Jan 2025. After period: Jan – Feb 2026.',
  });
}
