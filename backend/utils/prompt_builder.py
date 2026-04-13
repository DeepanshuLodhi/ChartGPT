STRICT_RULES = """
STRICT RULES - FOLLOW EXACTLY:
1. Output ONLY a valid JSON object with exactly two keys: "javascript" and "typescript". No extra text, no markdown, no code fences.
2. "javascript" value: ONLY "const option = { ... };" — no import statements, no extra code.
3. "typescript" value: MUST start with "import * as echarts from 'echarts';\\n" then "const option: echarts.EChartsOption = { ... };"
4. NEVER use new echarts.graphic.LinearGradient() — use gradient object: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#color1' }, { offset: 1, color: '#color2' }] }
5. NEVER use colorProfile — it does not exist in ECharts v5.
6. NEVER use xAxis.type 'time' with a data array — use xAxis.type 'category' with string array instead.
7. axisLabel.formatter must be a string like '{value} unit' — NEVER a JavaScript function.
8. NEVER add JS comments (// or /* */) anywhere inside the code strings.
9. NEVER leave empty arrays or placeholder comments — always use real sample numbers.
10. series[].name must exactly match legend.data entries when legend is used.
11. tooltip.trigger: use 'axis' for bar/line charts, use 'item' for pie/scatter/radar charts.
12. For pie charts: do NOT include xAxis or yAxis.
13. For radar charts: always include radar component with indicator: [{ name: string, max: number }].
14. For heatmap: always include visualMap component.
15. For markLine/markPoint: always nest inside the series object, not at top level.
16. NEVER use properties that do not exist in ECharts v5 official API.
17. All generated code must render without errors in the Apache ECharts example editor.
18. For dashed lines use lineStyle: { type: 'dashed' } inside the series object.
19. For multiple series always include legend component with data array matching all series names.
20. grid.containLabel must always be true to prevent label clipping.
"""

SAMPLE_DATA_RULES = """
SAMPLE DATA RULES:
- Always populate all data arrays with realistic numbers relevant to the chart topic.
- Category axis data examples: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] or ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].
- Value data examples: [120, 200, 150, 80, 70, 110, 130].
- Pie data format: [{ name: 'Category A', value: 335 }, { name: 'Category B', value: 310 }].
- Scatter data format: [[10, 20], [15, 35], [20, 10], [25, 45], [30, 28]].
- Radar data format: { value: [80, 70, 90, 60, 85], name: 'Series A' }.
- NEVER leave any array empty. NEVER use null or undefined as data values.
"""

OUTPUT_FORMAT = """
OUTPUT FORMAT — return exactly this JSON structure and absolutely nothing else:
{
  "javascript": "const option = { ... };",
  "typescript": "import * as echarts from 'echarts';\\nconst option: echarts.EChartsOption = { ... };"
}
"""


def build_text_prompt(user_input: str, retrieved_docs: list[str]) -> str:
    context = "\n\n".join(retrieved_docs)

    prompt = f"""You are an expert Apache ECharts v5 code generator. Your output must work perfectly in the Apache ECharts example editor without any errors.

{STRICT_RULES}

{SAMPLE_DATA_RULES}

ECHARTS V5 DOCUMENTATION CONTEXT:
{context}

USER REQUEST:
{user_input}

{OUTPUT_FORMAT}"""

    return prompt


def build_structured_prompt(chart_type: str, features: list[str], data: dict, retrieved_docs: list[str]) -> str:
    context = "\n\n".join(retrieved_docs)
    features_str = ", ".join(features) if features else "none"
    data_str = str(data) if data else "use realistic sample data"

    prompt = f"""You are an expert Apache ECharts v5 code generator. Your output must work perfectly in the Apache ECharts example editor without any errors.

{STRICT_RULES}

{SAMPLE_DATA_RULES}

ECHARTS V5 DOCUMENTATION CONTEXT:
{context}

USER SELECTED INPUTS:
- Chart Type: {chart_type}
- Features: {features_str}
- Data: {data_str}

{OUTPUT_FORMAT}"""

    return prompt


def build_image_prompt(chart_description: str, retrieved_docs: list[str]) -> str:
    context = "\n\n".join(retrieved_docs)

    prompt = f"""You are an expert Apache ECharts v5 code generator. Your output must work perfectly in the Apache ECharts example editor without any errors.

{STRICT_RULES}

IMAGE DATA RULES:
- Extract approximate data values from the chart description provided.
- If exact values are unclear use realistic estimated numbers that match the described trend.
- NEVER leave data arrays empty. Always fill them with real numbers.
- Match the number of data points to the number of x-axis categories described.
- For multiple series described in the image always include legend with all series names.
- For benchmark or reference lines use a separate series with lineStyle: {{ type: 'dashed' }}.

ECHARTS V5 DOCUMENTATION CONTEXT:
{context}

CHART DESCRIPTION EXTRACTED FROM IMAGE:
{chart_description}

{OUTPUT_FORMAT}"""

    return prompt