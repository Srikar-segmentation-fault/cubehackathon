"""Day 1 verification helper (not a deliverable, not part of the eval
harness): exercises the full Input -> Perception -> Uncertainty -> Policy
-> Audit pipeline with a MOCKED VLM response, so the policy engine
(uncertainty gate, condition mapper, disposition rules) can be verified
end-to-end without a live API key.

This does not replace the real evaluation harness (Day 2 scope) — it's a
one-off smoke test to prove Day 1's skeleton wiring is correct.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rtn.perception.fusion import EmbeddingFusion, FusionSignal  # noqa: E402
from rtn.perception.vlm_client import PerceptionResult, VLMClient  # noqa: E402
from rtn.pipeline import RTNPipeline  # noqa: E402
from rtn.schemas.enums import (  # noqa: E402
    EvidenceQuality,
    IdentityVerdict,
    PartStatus,
    SealStatus,
    StructuralDamageLevel,
    UsageSignLevel,
)
from rtn.schemas.vlm_output import (  # noqa: E402
    ComponentObservation,
    ConditionObservation,
    IdentityObservation,
    VLMResponse,
)
from scripts.run_single_unit import load_unit  # noqa: E402


class MockVLMClient(VLMClient):
    """Bypasses the real network call entirely and returns a canned,
    schema-valid VLMResponse, so the rest of the pipeline (gates, policy
    rules, evidence write) runs against a realistic payload."""

    def __init__(self) -> None:  # deliberately skip VLMClient.__init__ (no OpenAI client needed)
        self._model = "mock-vlm-v0"

    def evaluate_unit(self, unit) -> PerceptionResult:  # noqa: ANN001
        response = VLMResponse(
            identity=IdentityObservation(
                verdict=IdentityVerdict.MATCH,
                matching_attributes=["same bottle shape", "same cap color (steel blue)"],
                conflicting_attributes=[],
                evidence_quality=EvidenceQuality.GOOD,
                confidence=0.91,
                detail="Returned bottle matches the reference catalogue image in shape, "
                "cap color, and proportions.",
            ),
            completeness=[
                ComponentObservation(
                    part_name="bottle_body",
                    status=PartStatus.PRESENT,
                    evidence_quality=EvidenceQuality.GOOD,
                    confidence=0.95,
                    detail="Bottle body clearly visible and intact in the returned photo.",
                ),
                ComponentObservation(
                    part_name="screw_lid",
                    status=PartStatus.PRESENT,
                    evidence_quality=EvidenceQuality.GOOD,
                    confidence=0.9,
                    detail="Screw lid visible attached to the bottle neck.",
                ),
                ComponentObservation(
                    part_name="silicone_base_ring",
                    status=PartStatus.NOT_OBSERVED,
                    evidence_quality=EvidenceQuality.PARTIAL,
                    confidence=0.4,
                    detail="Base of the bottle is only partially visible in the provided "
                    "photo; cannot confirm presence or absence of the base ring.",
                ),
            ],
            condition=ConditionObservation(
                seal_status=SealStatus.OPENED,
                packaging_state_detail="No original packaging visible in the photo; item "
                "photographed unpackaged.",
                usage_signs=UsageSignLevel.LIGHT,
                usage_signs_detail="A visible scuff/dent mark on the mid-body section.",
                structural_damage=StructuralDamageLevel.MINOR,
                structural_damage_detail="Small dent visible on the body, does not appear "
                "to breach the wall.",
                functional_signs_positive=["body appears intact aside from the dent"],
                functional_signs_negative=[],
                evidence_quality=EvidenceQuality.GOOD,
                confidence=0.85,
            ),
            overall_notes=None,
        )
        return PerceptionResult(
            ok=True, response=response, model_version=self._model, latency_ms=123, raw_text=None
        )


def main() -> None:
    fixture_dir = REPO_ROOT / "data" / "fixtures" / "unit_001"
    unit = load_unit(fixture_dir)

    pipeline = RTNPipeline(vlm_client=MockVLMClient(), fusion=EmbeddingFusion())
    record = pipeline.run_unit(unit)

    print(record.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
