import os
import json
import requests

CACHE_FILE = os.path.join(os.path.dirname(__file__), "echarts_docs_cache.json")

BASE_URL = "https://raw.githubusercontent.com/apache/echarts-doc/master"

URLS = [
    f"{BASE_URL}/en/option/component/title.md",
    f"{BASE_URL}/en/option/component/legend.md",
    f"{BASE_URL}/en/option/component/grid.md",
    f"{BASE_URL}/en/option/component/x-axis.md",
    f"{BASE_URL}/en/option/component/y-axis.md",
    f"{BASE_URL}/en/option/component/tooltip.md",
    f"{BASE_URL}/en/option/component/toolbox.md",
    f"{BASE_URL}/en/option/component/data-zoom.md",
    f"{BASE_URL}/en/option/component/visual-map.md",
    f"{BASE_URL}/en/option/component/mark-line.md",
    f"{BASE_URL}/en/option/component/mark-point.md",
    f"{BASE_URL}/en/option/component/mark-area.md",
    f"{BASE_URL}/en/option/series/bar.md",
    f"{BASE_URL}/en/option/series/line.md",
    f"{BASE_URL}/en/option/series/pie.md",
    f"{BASE_URL}/en/option/series/scatter.md",
    f"{BASE_URL}/en/option/series/radar.md",
    f"{BASE_URL}/en/option/series/funnel.md",
    f"{BASE_URL}/en/option/series/gauge.md",
    f"{BASE_URL}/en/option/series/heatmap.md",
    f"{BASE_URL}/en/option/series/candlestick.md",
    f"{BASE_URL}/en/option/series/boxplot.md",
    f"{BASE_URL}/en/option/series/treemap.md",
    f"{BASE_URL}/en/option/series/sunburst.md",
    f"{BASE_URL}/en/option/series/graph.md",
    f"{BASE_URL}/en/option/series/sankey.md",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def chunk_text(text: str, chunk_size: int = 600) -> list[str]:
    lines = text.split("\n")
    chunks = []
    current = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        current += " " + line
        if len(current) >= chunk_size:
            chunks.append(current.strip())
            current = ""

    if current.strip():
        chunks.append(current.strip())

    return chunks


def scrape_echarts_docs() -> list[str]:
    if os.path.exists(CACHE_FILE):
        print("[RAG] Loading ECharts docs from cache...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("[RAG] Fetching ECharts v5 docs from GitHub...")
    all_chunks = []

    for url in URLS:
        try:
            print(f"[RAG] Fetching: {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                chunks = chunk_text(response.text)
                all_chunks.extend(chunks)
                print(f"[RAG] Got {len(chunks)} chunks from {url.split('/')[-1]}")
            else:
                print(f"[RAG] Skipped {url.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"[RAG] Failed {url.split('/')[-1]}: {e}")
            continue

    all_chunks = [c for c in all_chunks if len(c) > 80]
    print(f"[RAG] Total chunks: {len(all_chunks)}")

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"[RAG] Cached to {CACHE_FILE}")
    return all_chunks


def get_docs() -> list[str]:
    return scrape_echarts_docs()