const code = process.argv[2];
const isTypeScript = process.argv[3] === 'ts';

if (!code) {
  console.log(JSON.stringify({ valid: false, error: "No code provided" }));
  process.exit(0);
}

try {
  let stripped = code;

  // Strip TypeScript specific syntax
  if (isTypeScript) {
    stripped = stripped
      .replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '')
      .replace(/const\s+option\s*:\s*echarts\.EChartsOption\s*=/g, 'const option =')
      .replace(/const\s+option\s*:\s*\w+\s*=/g, 'const option =')
      .replace(/<[^>]+>/g, '')
      .trim();
  }

  // Strip const option = prefix to extract just the object
  stripped = stripped
    .replace(/const\s+option\s*=\s*/, '')
    .replace(/;$/, '')
    .trim();

  // Actually evaluate the option object
  const fn = new Function(`return ${stripped};`);
  const result = fn();

  if (typeof result !== 'object' || result === null) {
    console.log(JSON.stringify({ valid: false, error: "Result is not a valid object" }));
    process.exit(0);
  }

  const warnings = [];

  // Check series exists
  if (!result.series) {
    warnings.push("Missing series array");
  }

  if (Array.isArray(result.series)) {
    result.series.forEach((s, i) => {
      if (!s.type) {
        warnings.push(`series[${i}] missing type property`);
      }

      if (!s.data || (Array.isArray(s.data) && s.data.length === 0)) {
        warnings.push(`series[${i}] has empty or missing data`);
      }

      const noAxisTypes = ['pie', 'funnel', 'gauge', 'radar', 'treemap', 'sunburst'];

      if (!noAxisTypes.includes(s.type)) {
        if (!result.xAxis) warnings.push(`Missing xAxis for ${s.type} chart`);
        if (!result.yAxis) warnings.push(`Missing yAxis for ${s.type} chart`);
      }

      if (s.type === 'pie') {
        if (result.xAxis) warnings.push("pie chart should not have xAxis — remove it");
        if (result.yAxis) warnings.push("pie chart should not have yAxis — remove it");
      }

      if (s.type === 'radar' && !result.radar) {
        warnings.push("radar chart missing radar component with indicator array");
      }

      if (s.type === 'heatmap' && !result.visualMap) {
        warnings.push("heatmap missing visualMap component");
      }

      if (s.type === 'scatter') {
        if (result.xAxis && result.xAxis.type === 'category') {
          warnings.push("scatter chart xAxis should use type 'value' not 'category'");
        }
      }

      if (s.name && result.legend && Array.isArray(result.legend.data)) {
        if (!result.legend.data.includes(s.name)) {
          warnings.push(`series[${i}] name '${s.name}' not found in legend.data — they must match exactly`);
        }
      }

      if (s.yAxisIndex && !Array.isArray(result.yAxis)) {
        warnings.push(`series[${i}] uses yAxisIndex but yAxis is not an array`);
      }
    });
  }

  // Check for new echarts.graphic usage
  if (code.includes('new echarts')) {
    warnings.push("Contains 'new echarts.graphic' which is not valid in JSON config — use gradient object instead");
  }

  // Check for JS functions in formatter
  if (/"formatter"\s*:\s*function/.test(code) || /"formatter"\s*:\s*\(/.test(code)) {
    warnings.push("formatter must be a string template like '{value} unit' not a function");
  }

  // Check for arrow functions
  if (/=>\s*\{/.test(code) || /=>\s*\w/.test(code)) {
    warnings.push("Arrow functions are not valid in ECharts JSON config");
  }

  // Check for JS comments inside code
  if (/\/\/[^\n]*/.test(code) || /\/\*[\s\S]*?\*\//.test(code)) {
    warnings.push("JS comments found inside code — remove them for clean config");
  }

  // Check dual axis setup
  if (Array.isArray(result.yAxis) && Array.isArray(result.series)) {
    result.series.forEach((s, i) => {
      if (s.yAxisIndex !== undefined) {
        if (s.yAxisIndex >= result.yAxis.length) {
          warnings.push(`series[${i}] yAxisIndex ${s.yAxisIndex} out of range — yAxis only has ${result.yAxis.length} items`);
        }
      }
    });
  }

  console.log(JSON.stringify({ valid: true, warnings }));

} catch (e) {
  console.log(JSON.stringify({ valid: false, error: e.message }));
}