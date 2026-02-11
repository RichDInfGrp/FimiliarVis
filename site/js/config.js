// Fimiliar Vis — Brand tokens and Plotly configuration

export const COLORS = {
  main: '#0e0e0f',
  accent: '#93f3db',
  secondaryDark: '#5b5b5b',
  secondaryAccent: '#c8f9eb',
  light: '#F5F5F5',
  white: '#FFFFFF',
  positive: '#93f3db',
  negative: '#e07a5f',
  neutral: '#5b5b5b',
  gridline: '#E8E8E8',
};

export const CATEGORICAL = ['#93f3db', '#5b5b5b', '#66d9c2', '#0e0e0f', '#a0a0a0'];
export const SEQUENTIAL = ['#c8f9eb', '#93f3db', '#4ecab0', '#2a9d8f', '#1a6b5a'];
export const DIVERGING = ['#e07a5f', '#F5F5F5', '#93f3db'];

export const FONT = 'Inter, -apple-system, BlinkMacSystemFont, sans-serif';

// Plotly layout template (mirrors the Python "fimiliar" template)
export const PLOTLY_LAYOUT = {
  font: { family: FONT, color: COLORS.main, size: 13 },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  colorway: CATEGORICAL,
  title: { font: { size: 16, color: COLORS.main }, x: 0, xanchor: 'left' },
  legend: { orientation: 'h', yanchor: 'bottom', y: -0.2, xanchor: 'center', x: 0.5, font: { size: 12 } },
  xaxis: { gridcolor: COLORS.gridline, linecolor: COLORS.gridline, zeroline: false, tickfont: { size: 12 } },
  yaxis: { gridcolor: COLORS.gridline, linecolor: COLORS.gridline, zeroline: false, tickfont: { size: 12 } },
  hoverlabel: { font: { family: FONT, size: 12 } },
  hovermode: 'x unified',
  margin: { l: 60, r: 20, t: 50, b: 50 },
};

export const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };

export const USER_PROFILE = {
  name: 'Nicole Bello',
  title: 'Group Vice President, EMEA, Dayforce',
  location: 'London, England, United Kingdom',
  company: 'Dayforce',
  linkedinUrl: 'https://www.linkedin.com/in/nicolebello1/',
  photoUrl:
    'https://media.licdn.com/dms/image/v2/D4E03AQE2Z0fDBCK_fQ/' +
    'profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/' +
    '0/1715379076958?e=1772064000&v=beta&' +
    't=0Gdk3zA1oOXvGTsfBjPYyqq1ZxamBHD9JzeS88Nxf0c',
};

export const CREDENTIALS = { username: 'nicole.bello', password: 'fimiliar2026' };
