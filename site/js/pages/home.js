import { fetchData, renderPageHeader, renderKPIRow, renderSourceFooter } from '../components.js';

export async function render(container) {
  container.innerHTML = '';
  const kpis = await fetchData('kpis.json');

  renderPageHeader(container, '◆ Fimiliar Vis',
    'LinkedIn Performance Dashboard — tracking content impact, audience growth, and ICP engagement for Nicole Bello.');

  renderKPIRow(container, [
    { label: 'Impressions', value: kpis.impressions_total.toLocaleString() },
    { label: 'Members Reached', value: kpis.members_reached.toLocaleString() },
    { label: 'Total Posts', value: String(kpis.total_posts) },
    { label: 'Total Engagements', value: kpis.total_engagements.toLocaleString() },
  ]);

  renderKPIRow(container, [
    { label: 'ICP Contacts', value: String(kpis.icp_contacts) },
    { label: 'Unique Engagers', value: kpis.unique_engagers.toLocaleString() },
    { label: 'Followers', value: kpis.latest_followers.toLocaleString(), delta: `+${kpis.new_followers}` },
    { label: 'Avg Engagement Rate', value: `${kpis.avg_engagement_rate}%` },
  ]);

  container.insertAdjacentHTML('beforeend', '<hr class="divider">');

  container.insertAdjacentHTML('beforeend', `
    <h2 class="section-title">Dashboard Pages</h2>
    <div class="grid grid-2" style="margin-top:0.75rem;">
      <a class="nav-card" href="#content-performance">📊 Content Performance</a>
      <a class="nav-card" href="#audience-growth">📈 Audience Growth</a>
      <a class="nav-card" href="#audience-quality">🎯 Audience Quality</a>
      <a class="nav-card" href="#engagement-targets">🔥 Engagement Targets</a>
      <a class="nav-card" href="#network-growth">🌐 Network Growth</a>
      <a class="nav-card" href="#acquisition-velocity">⚡ Acquisition Velocity</a>
      <a class="nav-card" href="#icp-composition">🏢 ICP Composition</a>
      <a class="nav-card" href="#icp-engagement">🔬 ICP Engagement</a>
    </div>
    <style>
      .nav-card {
        display: block; padding: 1rem 1.25rem;
        background: var(--color-white); border-radius: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        text-decoration: none; color: var(--color-main);
        font-weight: 500; font-size: 15px;
        transition: box-shadow 0.2s, transform 0.15s;
      }
      .nav-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); transform: translateY(-1px); }
    </style>
  `);

  renderSourceFooter(container, {
    source: 'LinkedIn data via Fimiliar platform',
    updated: '2026-02-09',
    notes: 'Service period: 17 Jan 2026 – 9 Feb 2026. Data covers 48 posts, 189 contacts, 2,792 engagement records.',
  });
}
