// Fimiliar Vis — Reusable Plotly.js chart builders

import { PLOTLY_LAYOUT, PLOTLY_CONFIG, CATEGORICAL, SEQUENTIAL, COLORS } from './config.js';

function layout(overrides = {}) {
  return { ...PLOTLY_LAYOUT, ...overrides };
}

export function horizontalBar(el, data, { x, y, title = '', textFormat = ',.0f' } = {}) {
  const sorted = [...data].sort((a, b) => a[x] - b[x]);
  const trace = {
    type: 'bar',
    orientation: 'h',
    x: sorted.map((d) => d[x]),
    y: sorted.map((d) => d[y]),
    marker: { color: COLORS.accent },
    texttemplate: `%{x:${textFormat}}`,
    textposition: 'outside',
  };
  Plotly.newPlot(el, [trace], layout({ title: { text: title, ...PLOTLY_LAYOUT.title }, yaxis: { ...PLOTLY_LAYOUT.yaxis, automargin: true } }), PLOTLY_CONFIG);
}

export function lineChart(el, data, { x, y, title = '', colors = null } = {}) {
  const yFields = Array.isArray(y) ? y : [y];
  const traces = yFields.map((field, i) => ({
    type: 'scatter',
    mode: 'lines',
    x: data.map((d) => d[x]),
    y: data.map((d) => d[field]),
    name: field,
    line: { color: (colors || CATEGORICAL)[i % CATEGORICAL.length], width: 2 },
  }));
  Plotly.newPlot(el, traces, layout({ title: { text: title, ...PLOTLY_LAYOUT.title } }), PLOTLY_CONFIG);
}

export function areaChart(el, data, { x, y, color, title = '', normalize = false } = {}) {
  const categories = [...new Set(data.map((d) => d[color]))];
  const traces = categories.map((cat, i) => {
    const filtered = data.filter((d) => d[color] === cat);
    return {
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      stackgroup: 'one',
      groupnorm: normalize ? 'percent' : '',
      x: filtered.map((d) => d[x]),
      y: filtered.map((d) => d[y]),
      name: cat,
      line: { color: CATEGORICAL[i % CATEGORICAL.length] },
    };
  });
  Plotly.newPlot(el, traces, layout({ title: { text: title, ...PLOTLY_LAYOUT.title } }), PLOTLY_CONFIG);
}

export function donutChart(el, data, { values, names, title = '' } = {}) {
  const trace = {
    type: 'pie',
    hole: 0.55,
    values: data.map((d) => d[values]),
    labels: data.map((d) => d[names]),
    marker: { colors: CATEGORICAL },
    textposition: 'inside',
    textinfo: 'percent+label',
  };
  Plotly.newPlot(el, [trace], layout({ title: { text: title, ...PLOTLY_LAYOUT.title }, showlegend: false }), PLOTLY_CONFIG);
}

export function comboChart(el, data, { x, barY, lineY, barNames = null, lineNames = null, title = '' } = {}) {
  const barFields = Array.isArray(barY) ? barY : [barY];
  const lineFields = Array.isArray(lineY) ? lineY : [lineY];
  const bNames = barNames || barFields;
  const lNames = lineNames || lineFields;

  const traces = [];
  barFields.forEach((field, i) => {
    traces.push({
      type: 'bar',
      x: data.map((d) => d[x]),
      y: data.map((d) => d[field]),
      name: bNames[i],
      marker: { color: CATEGORICAL[i % CATEGORICAL.length] },
      yaxis: 'y',
    });
  });
  lineFields.forEach((field, i) => {
    traces.push({
      type: 'scatter',
      mode: 'lines',
      x: data.map((d) => d[x]),
      y: data.map((d) => d[field]),
      name: lNames[i],
      line: { color: CATEGORICAL[(i + barFields.length) % CATEGORICAL.length], width: 2 },
      yaxis: 'y2',
    });
  });

  Plotly.newPlot(el, traces, layout({
    title: { text: title, ...PLOTLY_LAYOUT.title },
    barmode: 'group',
    yaxis2: { overlaying: 'y', side: 'right', gridcolor: 'rgba(0,0,0,0)', tickfont: { size: 12 } },
  }), PLOTLY_CONFIG);
}

export function waterfallChart(el, categories, values, { title = '', measure = null } = {}) {
  const measures = measure || (['absolute', ...Array(values.length - 1).fill('relative')]);
  const trace = {
    type: 'waterfall',
    x: categories,
    y: values,
    measure: measures,
    increasing: { marker: { color: COLORS.positive } },
    decreasing: { marker: { color: COLORS.negative } },
    totals: { marker: { color: CATEGORICAL[3] } },
    textposition: 'outside',
    texttemplate: '%{y:+.0f}',
  };
  Plotly.newPlot(el, [trace], layout({ title: { text: title, ...PLOTLY_LAYOUT.title }, showlegend: false }), PLOTLY_CONFIG);
}

export function funnelChart(el, stages, values, { title = '' } = {}) {
  const trace = {
    type: 'funnel',
    y: stages,
    x: values,
    textinfo: 'value+percent initial',
    marker: { color: SEQUENTIAL.slice(0, stages.length) },
  };
  Plotly.newPlot(el, [trace], layout({ title: { text: title, ...PLOTLY_LAYOUT.title } }), PLOTLY_CONFIG);
}

export function scatterChart(el, data, { x, y, title = '', size = null } = {}) {
  const trace = {
    type: 'scatter',
    mode: 'markers',
    x: data.map((d) => d[x]),
    y: data.map((d) => d[y]),
    marker: {
      color: COLORS.accent,
      opacity: 0.7,
      size: size ? data.map((d) => Math.max(6, Math.sqrt(d[size]) / 2)) : 8,
    },
    text: data.map((d) => `${d[x]}, ${d[y]}`),
  };
  Plotly.newPlot(el, [trace], layout({ title: { text: title, ...PLOTLY_LAYOUT.title }, hovermode: 'closest' }), PLOTLY_CONFIG);
}
