import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

bifrost = OpenAI(
    base_url=f"{os.getenv('BIFROST_BASE_URL')}/openai",
    api_key=os.getenv("BIFROST_OPENAI_API_KEY"),
)

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

bifrost = OpenAI(
    base_url=f"{os.getenv('BIFROST_BASE_URL')}/openai",
    api_key=os.getenv("BIFROST_OPENAI_API_KEY"),
)

prompt = "What is the capital of France?"
for i in range(3):
    started = time.time()
    raw = bifrost.chat.completions.with_raw_response.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "x-bf-cache-key": "notebook-demo",
            "x-bf-cache-type": "direct",
        },
    )
    body = json.loads(raw.text)
    cache = body.get("extra_fields", {}).get("cache_debug", {})
    elapsed = time.time() - started
    print(f"call {i + 1}: {elapsed:.2f}s cache_debug={cache}")
    time.sleep(2)
