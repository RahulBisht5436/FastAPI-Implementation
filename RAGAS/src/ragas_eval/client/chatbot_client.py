from __future__ import annotations

import httpx

from ragas_eval.config import CHATBOT_BASE_URL, EVAL_SECRET, EVAL_TIMEOUT_SECONDS


def _raise_for_eval_response(response: httpx.Response) -> None:
    if response.status_code != 401:
        response.raise_for_status()
        return

    raise RuntimeError(
        "Eval request rejected with 401 Unauthorized. "
        "EVAL_SECRET in RAGAS/.env must exactly match personalChatBot/.env, "
        "and the backend must be restarted after changing it. "
        "If you previously ran `$env:EVAL_SECRET=...` before `uv run serve`, "
        "that stale shell value overrides .env until you restart the server in a fresh shell. "
        "You can also pass --eval-secret or set $env:EVAL_SECRET before running."
    ) from None


class ChatbotEvalClient:
    def __init__(
        self,
        base_url: str = CHATBOT_BASE_URL,
        eval_secret: str = EVAL_SECRET,
        timeout_seconds: float = EVAL_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.eval_secret = eval_secret
        self.timeout_seconds = timeout_seconds

    @property
    def _headers(self) -> dict[str, str]:
        return {"X-Eval-Secret": self.eval_secret}

    def health(self) -> dict:
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(
                f"{self.base_url}/eval/health",
                headers=self._headers,
            )
            _raise_for_eval_response(response)
            return response.json()

    def kb_status(self) -> dict:
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(
                f"{self.base_url}/eval/kb-status",
                headers=self._headers,
            )
            _raise_for_eval_response(response)
            return response.json()

    def run_eval(self, question: str) -> dict:
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/eval/run",
                headers=self._headers,
                json={"question": question},
            )
            _raise_for_eval_response(response)
            return response.json()
