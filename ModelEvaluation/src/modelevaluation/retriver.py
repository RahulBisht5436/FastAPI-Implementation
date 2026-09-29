import os
import re
import sys
import glob
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")  # loads OPENAI_API_KEY from .env

DATA_DIR = str(_PROJECT_ROOT / "data")
DB_DIR = str(_PROJECT_ROOT / "chroma_store")
INDEX_MARKER = Path(DB_DIR) / ".index_built"
# Cheapest OpenAI embedding model (per token vs text-embedding-3-large / ada-002).
EMBEDDING_MODEL = "text-embedding-3-small"
s
_TIMESTAMP_LINE = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")


def _session_from_path(path: str) -> str:
    match = re.search(r"lecture[_-]?(\d+)", path, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"Session[ _]*(\d+)", path, re.IGNORECASE)
    if match:
        return match.group(1)
    raise ValueError(f"Cannot extract session/lecture id from path: {path}")


def _should_skip_line(line: str, is_vtt: bool) -> bool:
    if not line:
        return True
    if is_vtt:
        return line == "WEBVTT" or "-->" in line
    return _TIMESTAMP_LINE.match(line) is not None


# 1. LOAD ---- read each transcript, strip cue/timestamp lines
def load_transcripts():
    docs = []
    paths = sorted(
        set(glob.glob(f"{DATA_DIR}/*.vtt") + glob.glob(f"{DATA_DIR}/lecture*.txt"))
    )

    for path in paths:
        is_vtt = path.lower().endswith(".vtt")
        lines = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if _should_skip_line(line, is_vtt):
                    continue
                lines.append(line)
        text = " ".join(lines)
        if not text.strip():
            continue

        session = _session_from_path(path)
        docs.append(Document(page_content=text, metadata={"session": session}))

    return docs


def _index_matches_current_model() -> bool:
    if not INDEX_MARKER.is_file():
        return False
    try:
        return INDEX_MARKER.read_text(encoding="utf-8").strip() == EMBEDDING_MODEL
    except OSError:
        return False


# 2. BUILD ---- chunk, embed once, and keep it on disk so we don't re-embed
def load_store():
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    if _index_matches_current_model():
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    if os.path.isdir(DB_DIR):
        shutil.rmtree(DB_DIR, ignore_errors=True)

    docs = load_transcripts()
    if not docs:
        raise ValueError(
            f"No transcript documents found under {DATA_DIR}/. "
            "Expected lecture*.txt or *.vtt files."
        )

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    ).split_documents(docs)

    if not chunks:
        raise ValueError("Text splitting produced no chunks.")

    store = Chroma.from_documents(chunks, embeddings, persist_directory=DB_DIR)
    INDEX_MARKER.parent.mkdir(parents=True, exist_ok=True)
    INDEX_MARKER.write_text(EMBEDDING_MODEL, encoding="utf-8")
    return store


def build_retriever():
    return load_store().as_retriever(search_kwargs={"k": 5})


# 3. TRY IT ---- python src/modelevaluation/retriver.py
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    retriever = build_retriever()

    results = retriever.invoke("what is regression testing?")

    for r in results:
        print(f"[Session {r.metadata['session']}] {r.page_content[:150]}...\n")
