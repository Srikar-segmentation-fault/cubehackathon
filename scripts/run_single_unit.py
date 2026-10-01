"""Day 1 CLI entrypoint: run the full pipeline for one fixture unit and
print the resulting evidence record.

Usage:
    python scripts/run_single_unit.py data/fixtures/unit_001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rtn.pipeline import RTNPipeline  # noqa: E402
from rtn.schemas.input import ExpectedComponent, ImageInput, OrderInfo, UnitInput  # noqa: E402


def load_unit(fixture_dir: Path) -> UnitInput:
    order_data = json.loads((fixture_dir / "order.json").read_text(encoding="utf-8"))
    components_data = json.loads((fixture_dir / "expected_components.json").read_text(encoding="utf-8"))

    images: list[ImageInput] = []
    ref_dir = fixture_dir / "reference"
    ret_dir = fixture_dir / "returned"
    for i, p in enumerate(sorted(ref_dir.glob("*"))):
        images.append(ImageInput(image_id=f"reference_{i+1}", role="reference", path=str(p)))
    for i, p in enumerate(sorted(ret_dir.glob("*"))):
        images.append(ImageInput(image_id=f"returned_{i+1}", role="returned", path=str(p)))

    return UnitInput(
        subject=order_data.get("subject", fixture_dir.name),
        organization_id=order_data.get("organization_id", "org-demo"),
        client_id=order_data.get("client_id", "client-demo"),
        operator_label=order_data.get("operator_label"),
        order=OrderInfo(
            sku=order_data["sku"],
            asin=order_data.get("asin"),
            product_name=order_data["product_name"],
            product_description=order_data.get("product_description"),
        ),
        expected_components=[ExpectedComponent(**c) for c in components_data],
        images=images,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RTN pipeline for one fixture unit.")
    parser.add_argument("fixture_dir", type=str, help="Path to a fixture directory (see data/fixtures/unit_001).")
    args = parser.parse_args()

    fixture_dir = Path(args.fixture_dir)
    if not fixture_dir.exists():
        raise SystemExit(f"fixture dir not found: {fixture_dir}")

    unit = load_unit(fixture_dir)
    pipeline = RTNPipeline()
    record = pipeline.run_unit(unit)

    print(record.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
