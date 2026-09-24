"""Apply Qdrant vector store + semantic cache config to Bifrost via config.json."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(cmd)}")


def main() -> None:
    run(["docker", "compose", "up", "-d", "qdrant", "bifrost"], check=False)
    run(["curl.exe", "-s", "http://localhost:8080/api/config"])


if __name__ == "__main__":
    main()
