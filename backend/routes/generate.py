from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag.vectorstore import retrieve
from utils.prompt_builder import build_text_prompt, build_structured_prompt
from utils.parser import parse_llm_response, clean_code
from utils.validator import validate_and_fix
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

LLM_MODEL = os.getenv("LLM_MODEL", "mistral")


class TextRequest(BaseModel):
    prompt: str


class StructuredRequest(BaseModel):
    chart_type: str
    features: list[str] = []
    data: dict = {}


def call_ollama(prompt: str) -> str:
    try:
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
        return response["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


@router.post("/text")
def generate_from_text(request: TextRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    retrieved_docs = retrieve(request.prompt)
    prompt = build_text_prompt(request.prompt, retrieved_docs)
    raw_response = call_ollama(prompt)
    result = parse_llm_response(raw_response)

    js_code, js_errors = validate_and_fix(result.get("javascript", ""), is_typescript=False)
    ts_code, ts_errors = validate_and_fix(result.get("typescript", ""), is_typescript=True)

    from utils.semantic_fixer import apply_semantic_fixes
    js_code, ts_code, semantic_fixes = apply_semantic_fixes(js_code, ts_code)

    return {
        "javascript": clean_code(js_code),
        "typescript": clean_code(ts_code),
        "retrieved_context": retrieved_docs,
        "validation_warnings": js_errors + ts_errors,
        "semantic_fixes": semantic_fixes
    }

@router.post("/structured")
def generate_from_structured(request: StructuredRequest):
    if not request.chart_type.strip():
        raise HTTPException(status_code=400, detail="Chart type cannot be empty")

    query = f"{request.chart_type} chart with {', '.join(request.features)}"
    retrieved_docs = retrieve(query)
    prompt = build_structured_prompt(
        request.chart_type, request.features, request.data, retrieved_docs
    )
    raw_response = call_ollama(prompt)
    result = parse_llm_response(raw_response)

    js_code, js_errors = validate_and_fix(result.get("javascript", ""), is_typescript=False)
    ts_code, ts_errors = validate_and_fix(result.get("typescript", ""), is_typescript=True)

    from utils.semantic_fixer import apply_semantic_fixes
    js_code, ts_code, semantic_fixes = apply_semantic_fixes(js_code, ts_code)

    return {
        "javascript": clean_code(js_code),
        "typescript": clean_code(ts_code),
        "retrieved_context": retrieved_docs,
        "validation_warnings": js_errors + ts_errors,
        "semantic_fixes": semantic_fixes
    }