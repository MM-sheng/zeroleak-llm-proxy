"""Standardized model diagnostics output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelDiagnostics:
    """Serializable diagnostic summary for one model output."""

    model_name: str
    probability: float
    diagnostics: dict[str, Any]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    summary: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize diagnostic fields."""
        if not self.model_name.strip():
            raise ValueError("model_name must be non-empty")
        probability = float(self.probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        object.__setattr__(self, "model_name", self.model_name.strip())
        object.__setattr__(self, "probability", probability)
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))
        if not self.summary:
            object.__setattr__(self, "summary", f"{self.model_name.strip()}: probability={probability:.4f}")

    def as_dict(self) -> dict[str, Any]:
        """Return a plain dictionary suitable for reports or JSON serialization."""
        return {
            "model_name": self.model_name,
            "probability": self.probability,
            "diagnostics": dict(self.diagnostics),
            "warnings": list(self.warnings),
            "summary": self.summary,
        }


def build_model_diagnostics(
    *,
    model_name: str,
    probability: float,
    diagnostics: dict[str, Any] | None = None,
    warnings: tuple[str, ...] | list[str] | None = None,
) -> ModelDiagnostics:
    """Build a standardized diagnostic summary from explicit fields."""
    return ModelDiagnostics(
        model_name=model_name,
        probability=probability,
        diagnostics=diagnostics or {},
        warnings=tuple(warnings or ()),
    )


def diagnostics_from_result(model_name: str, result: Any) -> ModelDiagnostics:
    """Build diagnostics from a model result object with common attributes."""
    if not hasattr(result, "probability"):
        raise ValueError("model result must expose a probability attribute")
    return build_model_diagnostics(
        model_name=model_name,
        probability=getattr(result, "probability"),
        diagnostics=getattr(result, "diagnostics", {}),
        warnings=getattr(result, "warnings", ()),
    )
