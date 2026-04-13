import json
import re


def extract_option_object(code: str) -> dict | None:
    try:
        stripped = code
        stripped = re.sub(r'import\s+.*?from\s+[\'"].*?[\'"];?\s*', '', stripped)
        stripped = re.sub(r'const\s+option\s*:\s*echarts\.EChartsOption\s*=', 'const option =', stripped)
        stripped = re.sub(r'const\s+option\s*=\s*', '', stripped)
        stripped = re.sub(r';\s*$', '', stripped.strip())
        stripped = re.sub(r'//[^\n]*', '', stripped)
        stripped = re.sub(r'/\*[\s\S]*?\*/', '', stripped)

        fn = None
        try:
            import subprocess, os
            js_eval = f"console.log(JSON.stringify({stripped}))"
            result = subprocess.run(
                ["node", "-e", js_eval],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout:
                return json.loads(result.stdout)
        except Exception:
            pass

        return None
    except Exception:
        return None


def get_data_range(data: list) -> tuple[float, float]:
    flat = []
    for d in data:
        if isinstance(d, (int, float)):
            flat.append(d)
        elif isinstance(d, dict) and 'value' in d:
            v = d['value']
            if isinstance(v, (int, float)):
                flat.append(v)
            elif isinstance(v, list):
                flat.extend([x for x in v if isinstance(x, (int, float))])
        elif isinstance(d, list):
            flat.extend([x for x in d if isinstance(x, (int, float))])
    if not flat:
        return 0, 100
    return min(flat), max(flat)


def ranges_are_incompatible(range1: tuple, range2: tuple, threshold: float = 3.0) -> bool:
    min1, max1 = range1
    min2, max2 = range2
    span1 = max(max1 - min1, 1)
    span2 = max(max2 - min2, 1)
    ratio = max(span1, span2) / max(min(span1, span2), 1)
    return ratio > threshold


def fix_legend_series_sync(option: dict) -> dict:
    series = option.get('series', [])
    if not series:
        return option

    series_names = [s.get('name') for s in series if s.get('name')]
    if not series_names:
        return option

    if 'legend' not in option:
        option['legend'] = {'data': series_names}
    else:
        option['legend']['data'] = series_names

    return option


def fix_dual_yaxis(option: dict) -> dict:
    series = option.get('series', [])
    no_axis_types = ['pie', 'funnel', 'gauge', 'radar', 'treemap', 'sunburst']

    eligible = [s for s in series if s.get('type') not in no_axis_types and s.get('data')]
    if len(eligible) < 2:
        return option

    ranges = [get_data_range(s['data']) for s in eligible]

    needs_dual = False
    for i in range(len(ranges)):
        for j in range(i + 1, len(ranges)):
            if ranges_are_incompatible(ranges[i], ranges[j]):
                needs_dual = True
                break

    if not needs_dual:
        return option

    current_yaxis = option.get('yAxis')
    if isinstance(current_yaxis, list) and len(current_yaxis) >= 2:
        return option

    yaxis_list = []
    assigned = {}

    for i, s in enumerate(eligible):
        r = ranges[i]
        span = max(r[1] - r[0], 1)
        padding = span * 0.1
        axis_min = max(0, round(r[0] - padding))
        axis_max = round(r[1] + padding)

        matched = None
        for ax_idx, ax_range in enumerate(yaxis_list):
            if not ranges_are_incompatible(r, ax_range['_range']):
                matched = ax_idx
                break

        if matched is None:
            axis_index = len(yaxis_list)
            yaxis_list.append({
                'type': 'value',
                'name': s.get('name', f'Axis {axis_index + 1}'),
                'min': axis_min,
                'max': axis_max,
                'axisLabel': {
                    'formatter': '{value}'
                },
                '_range': r
            })
            matched = axis_index

        assigned[i] = matched
        s['yAxisIndex'] = matched

    for ax in yaxis_list:
        ax.pop('_range', None)

    option['yAxis'] = yaxis_list

    return option


def fix_axis_ranges(option: dict) -> dict:
    series = option.get('series', [])
    no_axis_types = ['pie', 'funnel', 'gauge', 'radar', 'treemap', 'sunburst']

    eligible = [s for s in series if s.get('type') not in no_axis_types and s.get('data')]
    if not eligible:
        return option

    yaxis = option.get('yAxis')

    if isinstance(yaxis, dict):
        all_data = []
        for s in eligible:
            if not s.get('yAxisIndex'):
                all_data.extend(s['data'])
        if all_data:
            mn, mx = get_data_range(all_data)
            span = max(mx - mn, 1)
            padding = span * 0.1
            if 'min' not in yaxis:
                yaxis['min'] = max(0, round(mn - padding))
            if 'max' not in yaxis:
                yaxis['max'] = round(mx + padding)
        option['yAxis'] = yaxis

    elif isinstance(yaxis, list):
        for ax_idx, ax in enumerate(yaxis):
            ax_data = []
            for s in eligible:
                if s.get('yAxisIndex', 0) == ax_idx:
                    ax_data.extend(s['data'])
            if ax_data:
                mn, mx = get_data_range(ax_data)
                span = max(mx - mn, 1)
                padding = span * 0.1
                if 'min' not in ax:
                    ax['min'] = max(0, round(mn - padding))
                if 'max' not in ax:
                    ax['max'] = round(mx + padding)

    return option


def fix_pie_axes(option: dict) -> dict:
    series = option.get('series', [])
    has_pie = any(s.get('type') == 'pie' for s in series)
    if has_pie and len(series) == 1:
        option.pop('xAxis', None)
        option.pop('yAxis', None)
    return option


def fix_radar_component(option: dict) -> dict:
    series = option.get('series', [])
    has_radar = any(s.get('type') == 'radar' for s in series)
    if has_radar and 'radar' not in option:
        for s in series:
            if s.get('type') == 'radar' and s.get('data'):
                first = s['data'][0]
                if isinstance(first, dict) and 'value' in first:
                    values = first['value']
                    indicators = [{'name': f'Indicator {i+1}', 'max': max(values) * 1.2} for i in range(len(values))]
                    option['radar'] = {'indicator': indicators}
    return option


def fix_heatmap_visualmap(option: dict) -> dict:
    series = option.get('series', [])
    has_heatmap = any(s.get('type') == 'heatmap' for s in series)
    if has_heatmap and 'visualMap' not in option:
        all_values = []
        for s in series:
            if s.get('type') == 'heatmap' and s.get('data'):
                for d in s['data']:
                    if isinstance(d, list) and len(d) >= 3:
                        all_values.append(d[2])
        mn = min(all_values) if all_values else 0
        mx = max(all_values) if all_values else 100
        option['visualMap'] = {
            'min': mn,
            'max': mx,
            'calculable': True,
            'orient': 'horizontal',
            'left': 'center',
            'bottom': '15%'
        }
    return option


def fix_grid_contain_label(option: dict) -> dict:
    series = option.get('series', [])
    no_axis_types = ['pie', 'funnel', 'gauge', 'radar', 'treemap', 'sunburst']
    has_axis_chart = any(s.get('type') not in no_axis_types for s in series)
    if has_axis_chart:
        if 'grid' not in option:
            option['grid'] = {'containLabel': True}
        elif not option['grid'].get('containLabel'):
            option['grid']['containLabel'] = True
    return option


def option_to_js(option: dict) -> str:
    json_str = json.dumps(option, indent=2)
    json_str = json_str.replace('"type":', 'type:')
    return f"const option = {json_str};"


def option_to_ts(option: dict) -> str:
    json_str = json.dumps(option, indent=2)
    return f"import * as echarts from 'echarts';\nconst option: echarts.EChartsOption = {json_str};"


def rebuild_code_from_option(option: dict) -> tuple[str, str]:
    json_str = json.dumps(option, indent=2)
    js = f"const option = {json_str};"
    ts = f"import * as echarts from 'echarts';\nconst option: echarts.EChartsOption = {json_str};"
    return js, ts


def fix_radar_issues(option: dict) -> dict:
    series = option.get('series', [])
    has_radar = any(s.get('type') == 'radar' for s in series)

    if not has_radar:
        return option

    # Remove xAxis and yAxis from radar charts
    option.pop('xAxis', None)
    option.pop('yAxis', None)

    # Fix radar component - remove deprecated name property
    if 'radar' in option:
        option['radar'].pop('name', None)

    # Fix radar series data format
    # Radar data must be: [{ value: [...], name: 'series name' }]
    for s in series:
        if s.get('type') == 'radar' and s.get('data'):
            fixed_data = []
            for i, d in enumerate(s['data']):
                if isinstance(d, list):
                    fixed_data.append({
                        'value': d,
                        'name': f'Item {i + 1}'
                    })
                elif isinstance(d, dict):
                    fixed_data.append(d)
            s['data'] = fixed_data

    # Fix radar indicator to match data dimensions
    if 'radar' in option:
        radar = option['radar']
        for s in series:
            if s.get('type') == 'radar' and s.get('data'):
                first = s['data'][0]
                values = first.get('value', []) if isinstance(first, dict) else first
                if isinstance(values, list):
                    current_indicators = radar.get('indicator', [])
                    if len(current_indicators) != len(values):
                        radar['indicator'] = [
                            {'name': f'Indicator {i + 1}', 'max': max(values) * 1.2 if values else 100}
                            for i in range(len(values))
                        ]

    return option


def apply_semantic_fixes(js_code: str, ts_code: str) -> tuple[str, str, list[str]]:
    fixes_applied = []

    option = extract_option_object(js_code)
    if option is None:
        return js_code, ts_code, ["Could not parse option object for semantic fixing"]

    original = json.dumps(option)
    
    option = fix_radar_issues(option)
    if json.dumps(option) != original:
        fixes_applied.append("Fixed radar chart: removed xAxis/yAxis, fixed data format, removed deprecated name property")

    option = fix_pie_axes(option)
    if json.dumps(option) != original:
        fixes_applied.append("Removed xAxis/yAxis from pie chart")

    option = fix_legend_series_sync(option)
    if json.dumps(option) != original:
        fixes_applied.append("Synced legend.data with series names")

    option = fix_dual_yaxis(option)
    if json.dumps(option) != original:
        fixes_applied.append("Added dual yAxis for incompatible data ranges")

    option = fix_axis_ranges(option)
    option = fix_radar_component(option)
    option = fix_heatmap_visualmap(option)
    option = fix_grid_contain_label(option)

    js, ts = rebuild_code_from_option(option)
    return js, ts, fixes_applied