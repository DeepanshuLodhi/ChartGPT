import re
import json
import subprocess
import os

VALIDATOR_JS = os.path.join(os.path.dirname(__file__), "validate_chart.js")

REQUIRED_FIXES = [
    # Fix new echarts.graphic.LinearGradient with named args
    (
        r'new\s+echarts\.graphic\.LinearGradient\s*\(\s*x\s*:\s*(\d+)\s*,\s*y\s*:\s*(\d+)\s*,\s*x2\s*:\s*(\d+)\s*,\s*y2\s*:\s*(\d+)\s*,\s*colorStops\s*:\s*(\[[\s\S]*?\])\s*\)',
        r"{ type: 'linear', x: \1, y: \2, x2: \3, y2: \4, colorStops: \5 }"
    ),
    # Fix new echarts.graphic.LinearGradient with positional args
    (
        r'new\s+echarts\.graphic\.LinearGradient\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\[[\s\S]*?\])\s*\)',
        r"{ type: 'linear', x: \1, y: \2, x2: \3, y2: \4, colorStops: \5 }"
    ),
    # Remove backslash escaping artifacts
    (r'\\n', ' '),
    (r'\\\s*\n', '\n'),
    (r'\\(["\'])', r'\1'),
    # Remove JS comments
    (r'//[^\n"]*\n', '\n'),
    (r'/\*[\s\S]*?\*/', ''),
    # Fix trailing commas
    (r',(\s*[}\]])', r'\1'),
    # Remove colorProfile
    (r'colorProfile\s*:\s*[\'"][^\'"]*[\'"],?\s*', ''),
    # Remove formatter functions
    (r'formatter\s*:\s*function\s*\([^)]*\)\s*\{[^}]*\}', "formatter: '{value}'"),
    (r'formatter\s*:\s*\([^)]*\)\s*=>\s*\{[^}]*\}', "formatter: '{value}'"),
    (r'formatter\s*:\s*\([^)]*\)\s*=>[^,}\n]*', "formatter: '{value}'"),
]


def auto_fix_code(code: str) -> str:
    for pattern, replacement in REQUIRED_FIXES:
        code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    return code.strip()


def run_node_validator(code: str, is_typescript: bool = False) -> dict:
    try:
        args = ["node", VALIDATOR_JS, code]
        if is_typescript:
            args.append("ts")
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if result.stdout:
            return json.loads(result.stdout)
        return {"valid": False, "error": result.stderr or "Unknown error"}
    except subprocess.TimeoutExpired:
        return {"valid": False, "error": "Validator timed out"}
    except FileNotFoundError:
        return {"valid": False, "error": "Node.js not found"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def validate_and_fix(code: str, is_typescript: bool = False) -> tuple[str, list[str]]:
    fixed = auto_fix_code(code)
    result = run_node_validator(fixed, is_typescript)

    warnings = []
    if not result.get("valid"):
        error = result.get("error", "Unknown syntax error")
        warnings.append(f"Syntax error: {error}")
    else:
        warnings.extend(result.get("warnings", []))

    return fixed, warnings
