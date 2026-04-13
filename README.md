# ChartGPT — Multimodal AI System for Apache ECharts Code Generation

A fully local, open-source Generative AI application that converts natural language, structured inputs, and chart images into production-ready Apache ECharts v5 configurations in both JavaScript and TypeScript.

---

## Objective

Eliminate manual effort and trial-and-error when writing Apache ECharts configurations. ChartGPT uses a multimodal AI pipeline to understand user intent and generate valid, ready-to-use chart code that works directly in the Apache ECharts example editor.

---

## Features

- **Text to Chart** — Describe your chart in plain English and get ECharts v5 code instantly
- **Structured Input** — Select chart type, features, and data using a guided form
- **Image to Chart** — Upload any chart image and get the equivalent ECharts configuration
- **RAG-Based Generation** — Uses real Apache ECharts v5 documentation fetched from the official GitHub repository as knowledge base
- **Live Preview** — Renders the generated chart in real-time inside the app
- **Dual Output** — Always returns both JavaScript and TypeScript versions
- **Syntax Validation** — Node.js runtime executor catches real syntax errors before returning code
- **Semantic Fixing** — Automatically corrects logical issues like dual yAxis, legend sync, missing components
- **Auto Fix** — Converts invalid patterns like new echarts.graphic.LinearGradient() to correct JSON gradient objects automatically

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Mistral 7B via Ollama (local) |
| Vision Model | LLaVA via Ollama (local) |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| Vector Database | FAISS (in-memory) |
| RAG Framework | LangChain |
| Backend | FastAPI (Python) |
| Frontend | Angular 20 + ngx-echarts |
| Code Validation | Node.js runtime execution |
| Doc Source | apache/echarts-doc GitHub (raw markdown) |

Everything runs 100% locally. No API keys, no cloud, no billing.

---

## System Architecture

```
User Input (Text / Structured / Image)
         |
[INPUT LAYER]
  Text      -> Natural language prompt
  Structured -> Chart type + features + data form
  Image     -> LLaVA vision model -> text description
         |
[RAG LAYER]
  Query -> FAISS vector store
  Top 3 relevant ECharts v5 doc chunks retrieved
  Source: apache/echarts-doc GitHub repository (real markdown files)
         |
[PROMPT BUILDER]
  User intent + retrieved docs -> structured prompt
  Strict rules injected to prevent hallucination and invalid syntax
         |
[LLM - Mistral 7B via Ollama]
  Generates raw JSON with javascript and typescript keys
         |
[PARSER]
  Strips markdown fences
  Extracts JSON object
  Auto-closes truncated brackets from token limit cuts
         |
[SYNTAX FIXER]
  Converts new echarts.graphic.LinearGradient() -> JSON gradient object
  Removes JS comments // and /* */
  Fixes trailing commas before } and ]
  Removes non-existent properties like colorProfile
         |
[NODE.JS VALIDATOR]
  Actually executes the code in Node.js runtime
  Catches real syntax errors
  Validates ECharts structure: missing series, wrong axis types, etc.
  Separate JS and TS handling
         |
[SEMANTIC FIXER]
  Syncs legend.data with series names automatically
  Detects incompatible data ranges -> adds dual yAxis
  Fixes axis min/max based on actual data values
  Adds missing radar indicator component
  Adds missing heatmap visualMap component
  Ensures grid.containLabel: true
  Removes xAxis/yAxis from pie charts
  Rebuilds clean JS and TS from fixed option object
         |
[FINAL OUTPUT]
  javascript: "const option = { ... };"
  typescript: "import * as echarts from 'echarts'; const option: echarts.EChartsOption = { ... };"
  validation_warnings: [ ... ]
  semantic_fixes: [ ... ]
         |
[ANGULAR FRONTEND]
  Live ECharts preview via ngx-echarts
  JS/TS tabs with copy button
  Validation warnings displayed
```

---

## Project Structure

```
ChartGPT/
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── .env                        # Environment config
│   ├── requirements.txt
│   ├── rag/
│   │   ├── echarts_docs.py         # Fetches ECharts v5 docs from GitHub
│   │   └── vectorstore.py          # FAISS index builder and retriever
│   ├── routes/
│   │   ├── generate.py             # Text and structured input endpoints
│   │   └── image.py                # Image upload endpoint
│   └── utils/
│       ├── prompt_builder.py       # Prompt templates with strict rules
│       ├── parser.py               # LLM response parser with auto-fix
│       ├── validator.py            # Syntax fixer + Node.js validator
│       ├── validate_chart.js       # Node.js chart validation script
│       └── semantic_fixer.py       # Semantic correctness fixer
└── frontend/
    └── chartgpt-ui/
        └── src/app/
            ├── pages/
            │   ├── home/           # Landing page
            │   ├── text-to-chart/  # Text input page
            │   ├── structured-input/ # Form input page
            │   └── image-upload/   # Image upload page
            ├── components/
            │   ├── code-output/    # JS/TS tabs with copy button
            │   └── chart-preview/  # Live ECharts renderer
            └── services/
                └── chart.ts        # HTTP service for API calls
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Angular CLI: npm install -g @angular/cli
- Ollama: https://ollama.com/download

### 1. Pull Ollama models

```bash
ollama pull mistral
ollama pull llava
```

### 2. Setup backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Run backend

```bash
uvicorn main:app --reload --port 8000
```

First run will automatically fetch and cache ECharts v5 documentation from GitHub and download the sentence-transformers embedding model.

### 4. Setup and run frontend

```bash
cd frontend/chartgpt-ui
npm install
ng serve
```

Open http://localhost:4200

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/generate/text | Generate from natural language |
| POST | /api/generate/structured | Generate from form inputs |
| POST | /api/image/upload | Generate from chart image |
| GET | /docs | Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/api/generate/text \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Bar chart showing monthly sales for Jan to Jun with tooltip and gradient colors"}'
```

### Example Response

```json
{
  "javascript": "const option = { ... };",
  "typescript": "import * as echarts from 'echarts';\nconst option: echarts.EChartsOption = { ... };",
  "validation_warnings": [],
  "semantic_fixes": ["Synced legend.data with series names"],
  "retrieved_context": ["..."]
}
```

---

## Environment Variables

File: backend/.env

```
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=mistral
VISION_MODEL=llava
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## Known Limitations

- **Image accuracy** — LLaVA is a small local vision model and may misread axis labels or series names from complex chart images. This is a known limitation of running inference locally without a GPU.
- **Generation speed** — Mistral 7B runs on CPU by default. Expect 30 to 90 seconds per generation. Speed improves significantly with a GPU.
- **Semantic correctness** — The semantic fixer handles common issues but complex custom chart configurations may still require minor manual adjustments.
- **Token limit** — Long or complex prompts may hit the 2048 token output limit. The parser auto-closes truncated brackets but very complex charts may need retrying.

---

## How Live Preview Works

The Angular frontend uses new Function() to evaluate the generated JavaScript option object in the browser runtime and passes it directly to ngx-echarts for rendering. This means the preview renders even if the code has minor issues that strict TypeScript would reject. The copy-paste code in the output panel is the fully validated and semantically fixed version intended for use in production or the Apache ECharts example editor.

---

## Resume Highlights

- Built end-to-end multimodal AI pipeline from scratch using only free and open-source tools
- Implemented RAG system using real documentation scraped from apache/echarts-doc GitHub repository
- Designed 5-stage output quality pipeline: Parse -> Syntax Fix -> Node.js Validate -> Semantic Fix -> Rebuild
- Integrated local LLM (Mistral 7B) and Vision model (LLaVA) via Ollama with zero cloud dependency
- Built Angular 20 frontend with live ECharts chart preview, JS/TS code output, and copy functionality
- Deployed entirely on local machine with no API keys, no billing, and no data sent to external services
