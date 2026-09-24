import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

BASE = os.getenv("BIFROST_BASE_URL")
GROQ_MODEL = "groq/openai/gpt-oss-20b"
GROQ_FALLBACK = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=f"{BASE}/openai",
    api_key=os.getenv("BIFROST_GROQ_API_KEY"),
)

raw = client.chat.completions.with_raw_response.create(
    model=GROQ_MODEL,
    messages=[{"role": "user", "content": "Say hello in one word."}],
    extra_body={"fallbacks": [GROQ_FALLBACK]},
    extra_headers={"x-bf-cache-key": "fallback-test", "x-bf-cache-no-store": "true"},
)

body = json.loads(raw.text)
extra = body.get("extra_fields", {})
print("status ok")
print("provider=", extra.get("provider"))
print("resolved_model=", extra.get("resolved_model_used"))
print("fallback_index=", raw.headers.get("x-bifrost-fallback-index", "0 (primary)"))
print("content=", body["choices"][0]["message"]["content"])
