"""One-off verification helper (not a deliverable): exercises the running
FastAPI server's /units/evaluate-upload endpoint with a real image and the
real Groq VLM, to confirm the frontend's upload path works end-to-end
before testing in the browser.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    image_path = REPO_ROOT / "data" / "fixtures" / "unit_001" / "reference" / "towel.jpg"
    if not image_path.exists():
        print(f"FAIL: test image not found at {image_path}")
        sys.exit(1)

    data = {
        "subject": "SMOKE-TEST-API-1",
        "sku": "SKU-TEST",
        "product_name": "Test product (towel)",
        "organization_id": "org-demo",
        "client_id": "client-demo",
        "expected_components_json": "[]",
    }
    with open(image_path, "rb") as f:
        files = [("reference_files", (image_path.name, f, "image/jpeg"))]
        resp = requests.post(
            "http://127.0.0.1:8000/units/evaluate-upload", data=data, files=files, timeout=90
        )

    print("status_code:", resp.status_code)
    print(resp.text[:3000])


if __name__ == "__main__":
    main()
