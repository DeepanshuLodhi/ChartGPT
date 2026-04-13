from unittest import result

from fastapi import APIRouter, HTTPException, UploadFile, File
from rag.vectorstore import retrieve
from utils.prompt_builder import build_image_prompt
from utils.parser import parse_llm_response, clean_code
from utils.validator import validate_and_fix
import ollama
import os
import base64
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

VISION_MODEL = os.getenv("VISION_MODEL", "llava")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")


def describe_image_with_llava(image_bytes: bytes) -> str:
    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": """Analyze this chart image and extract the following information:
1. Chart type (bar, line, pie, scatter, etc.)
2. Title if visible
3. X-axis label and categories/values if visible
4. Y-axis label and range if visible
5. Series names if visible
6. Approximate data values
7. Colors used
8. Any other visual features (legend, tooltip, grid, stacked, smooth, etc.)

Respond in plain text with clear labels for each point.""",
                    "images": [image_b64],
                }
            ],
        )
        return response["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision model error: {str(e)}")


def generate_code_from_description(description: str) -> dict:
    try:
        retrieved_docs = retrieve(description)
        prompt = build_image_prompt(description, retrieved_docs)

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an Apache ECharts v5 expert. Always respond with valid JSON only. No markdown, no explanation. No import statements in javascript output.",
                },
                {"role": "user", "content": prompt},
            ],
            options={"num_predict": 2048, "temperature": 0.1, "timeout": 300},
        )

        raw = response["message"]["content"]
        result = parse_llm_response(raw)

        js_code, js_errors = validate_and_fix(result.get("javascript", ""), is_typescript=False)
        ts_code, ts_errors = validate_and_fix(result.get("typescript", ""), is_typescript=True)

        from utils.semantic_fixer import apply_semantic_fixes
        js_code, ts_code, semantic_fixes = apply_semantic_fixes(js_code, ts_code)

        result["javascript"] = js_code
        result["typescript"] = ts_code
        result["validation_warnings"] = js_errors + ts_errors
        result["semantic_fixes"] = semantic_fixes

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation error: {str(e)}")


@router.post("/upload")
async def generate_from_image(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG, PNG, WEBP or GIF.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size must be under 10MB")

    print("[Image] Describing image with LLaVA...")
    description = describe_image_with_llava(image_bytes)
    print(f"[Image] Description: {description}")

    print("[Image] Generating ECharts code from description...")
    result = generate_code_from_description(description)

    return {
        "description": description,
        "javascript": clean_code(result.get("javascript", "")),
        "typescript": clean_code(result.get("typescript", "")),
        "validation_warnings": result.get("validation_warnings", [])
    }