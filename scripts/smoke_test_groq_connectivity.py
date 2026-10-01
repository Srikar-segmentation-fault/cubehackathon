"""One-off verification helper (not a deliverable): confirms the configured
VLM provider (Groq by default) is reachable and authenticated, using a
plain text-only chat completion — no images, no structured output. This
isolates connectivity/auth problems from vision-path or schema problems.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from openai import OpenAI  # noqa: E402

from rtn.config import settings  # noqa: E402


def main() -> None:
    if not settings.vlm_api_key or settings.vlm_api_key == "gsk_...":
        print("FAIL: VLM_API_KEY is not set in .env (still a placeholder).")
        sys.exit(1)

    print(f"Using base_url={settings.vlm_base_url}, model={settings.vlm_model}")
    client = OpenAI(api_key=settings.vlm_api_key, base_url=settings.vlm_base_url)

    try:
        completion = client.chat.completions.create(
            model=settings.vlm_model,
            timeout=settings.vlm_timeout_seconds,
            messages=[
                {"role": "user", "content": "Reply with exactly one word: OK"},
            ],
            max_completion_tokens=10,
        )
        content = completion.choices[0].message.content
        print("SUCCESS: model responded ->", repr(content))
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {type(exc).__name__}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
