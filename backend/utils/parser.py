import json
import re


def fix_common_errors(code: str) -> str:
    # Fix unclosed strings in formatter
    code = re.sub(
        r"formatter:\s*'([^']*)\n", lambda m: f"formatter: '{m.group(1)}',\n", code
    )
    # Remove JS comments
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # Fix trailing commas before closing braces
    code = re.sub(r",\s*}", "}", code)
    code = re.sub(r",\s*]", "]", code)
    return code.strip()


def parse_llm_response(response: str) -> dict:
    response = response.strip()

    response = re.sub(r"^```(?:json)?\s*", "", response)
    response = re.sub(r"\s*```$", "", response)
    response = response.strip()

    try:
        parsed = json.loads(response)
        if "javascript" in parsed and "typescript" in parsed:
            js = parsed["javascript"]
            ts = parsed["typescript"]
            if js.count("{") != js.count("}"):
                diff = js.count("{") - js.count("}")
                js += "}" * diff + ";"
            if ts.count("{") != ts.count("}"):
                diff = ts.count("{") - ts.count("}")
                ts += "}" * diff + ";"
            parsed["javascript"] = fix_common_errors(js)
            parsed["typescript"] = fix_common_errors(ts)
            return parsed
    except json.JSONDecodeError:
        pass

    json_match = re.search(
        r'\{[\s\S]*?"javascript"[\s\S]*?"typescript"[\s\S]*?\}(?=\s*$)', response
    )
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            if "javascript" in parsed and "typescript" in parsed:
                parsed["javascript"] = fix_common_errors(parsed["javascript"])
                parsed["typescript"] = fix_common_errors(parsed["typescript"])
                return parsed
        except json.JSONDecodeError:
            pass

    code_block_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", response)
    if code_block_match:
        try:
            parsed = json.loads(code_block_match.group(1))
            if "javascript" in parsed and "typescript" in parsed:
                parsed["javascript"] = fix_common_errors(parsed["javascript"])
                parsed["typescript"] = fix_common_errors(parsed["typescript"])
                return parsed
        except json.JSONDecodeError:
            pass

    js_match = re.search(r"const option\s*=\s*(\{[\s\S]*)", response)
    if js_match:
        raw = js_match.group(1)
        open_count = raw.count("{")
        close_count = raw.count("}")
        if open_count > close_count:
            raw += "}" * (open_count - close_count)
        raw = raw.rstrip(";").strip()
        js_code = f"const option = {raw};"
        ts_code = f"import * as echarts from 'echarts';\nconst option: echarts.EChartsOption = {raw};"
        return {
            "javascript": fix_common_errors(js_code),
            "typescript": fix_common_errors(ts_code),
        }

    return {
        "javascript": "// Failed to parse response. Please try again.",
        "typescript": "// Failed to parse response. Please try again.",
        "raw": response,
    }


def clean_code(code: str) -> str:
    code = code.replace("\\n", "\n")
    code = code.replace('\\"', '"')
    return code.strip()
