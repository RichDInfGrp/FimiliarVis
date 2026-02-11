import { fetchData, renderPageHeader, renderKPIRow, renderChartWithCaption, renderSectionTitle, renderSourceFooter } from '../components.js';
import { lineChart, areaChart, waterfallChart } from '../charts.js';

export async function render(container) {
  container.innerHTML = '';
  const [icpFirstSeen, weeklyIcp, weeklyShare] = await Promise.all([
    fetchData('icp_first_seen.json'),
    fetchData('weekly_icp.json'),
    fetchData('weekly_share.json'),
  ]);

  renderPageHeader(container, 'Network Growth',
    "How Nicole's ICP network is expanding over time — based on first engagement date as a proxy for when contacts entered her orbit.");

  const totalIcp = icpFirstSeen.length;
  const weeks = weeklyIcp.length;
  const rate = weeks > 0 ? (totalIcp / weeks).toFixed(1) : '0';
  const latest = icpFirstSeen.length ? icpFirstSeen[icpFirstSeen.length - 1].first_engagement : 'N/A';

  renderKPIRow(container, [
    { label: 'Total ICP Engagers', value: String(totalIcp) },
    { label: 'ICP per Week (avg)', value: rate },
    { label: 'Weeks of Data', value: String(weeks) },
    { label: 'Latest ICP Engagement', value: typeof latest === 'string' ? latest.split('T')[0] : latest },
  ]);

  // Cumulative ICP
  renderSectionTitle(container, 'Cumulative ICP Engagers Over Time');
  if (icpFirstSeen.length) {
    const dateMap = {};
    icpFirstSeen.forEach((d) => {
      const dt = d.first_engagement?.split('T')[0];
      if (dt) dateMap[dt] = (dateMap[dt] || 0) + 1;
    });
    let cum = 0;
    const cumData = Object.entries(dateMap).sort().map(([date, count]) => {
      cum += count;
      return { date, cumulative_icp: cum };
    });
    const cumEl = renderChartWithCaption(container, 'chart-cumulative',
      'Each ICP contact counted at their first engagement date. This is a proxy — actual connection dates are unavailable.');
    lineChart(cumEl, cumData, { x: 'date', y: 'cumulative_icp', title: 'Cumulative ICP Engagers (First Engagement Date)' });
  }

  // ICP share area
  renderSectionTitle(container, 'ICP vs Non-ICP Engagement Share');
  if (weeklyShare.length) {
    const shareEl = renderChartWithCaption(container, 'chart-share', 'ICP share of total weekly engagement activity.');
    areaChart(shareEl, weeklyShare, { x: 'week', y: 'engagements', color: 'category', title: 'ICP vs Non-ICP Engagement Share', normalize: true });
  }

  // Waterfall
  renderSectionTitle(container, 'Weekly ICP Growth Waterfall');
  if (weeklyIcp.length > 1) {
    const labels = weeklyIcp.map((w) => {
      const d = new Date(w.week);
      return d.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
    });
    const values = weeklyIcp.map((w) => w.unique_icp_engagers);
    const wfEl = renderChartWithCaption(container, 'chart-waterfall', 'Net new unique ICP engagers each week.');
    waterfallChart(wfEl, labels, values, { title: 'Weekly New ICP Engagers' });
  }

  renderSourceFooter(container, {
    source: 'Engagement data enriched with Contacts',
    updated: '2026-02-09',
    notes: 'First engagement date used as proxy for ICP network entry. Connection dates are not available in the source data.',
  });
}
