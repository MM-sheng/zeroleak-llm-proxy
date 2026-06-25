"""Ensemble probability model."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


@dataclass(frozen=True)
class ModelProbability:
    """One model probability contribution to an ensemble."""

    name: str
    probability: float
    weight: float = 1.0
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate and normalize one model contribution."""
        if not self.name.strip():
            raise ValueError("model name must be non-empty")
        probability = float(self.probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("model probability must be between 0 and 1")
        weight = float(self.weight)
        if weight <= 0:
            raise ValueError("model weight must be positive")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "probability", probability)
        object.__setattr__(self, "weight", weight)
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))


@dataclass(frozen=True)
class EnsembleProbabilityResult:
    """Weighted ensemble probability output."""

    probability: float
    components: tuple[ModelProbability, ...]
    normalized_weights: dict[str, float]
    diagnostics: dict[str, float | int]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def combine_model_probabilities(
    components: list[ModelProbability] | tuple[ModelProbability, ...],
    *,
    disagreement_threshold: float = 0.25,
) -> EnsembleProbabilityResult:
    """Combine model probabilities with normalized positive weights."""
    if not components:
        raise ValueError("at least one model probability is required")
    if disagreement_threshold < 0:
        raise ValueError("disagreement_threshold must be non-negative")

    normalized_components = tuple(
        component if isinstance(component, ModelProbability) else ModelProbability(**component)
        for component in components
    )
    total_weight = sum(component.weight for component in normalized_components)
    if total_weight <= 0:
        raise ValueError("total model weight must be positive")

    normalized_weights = {
        component.name: component.weight / total_weight
        for component in normalized_components
    }
    probability = sum(
        component.probability * normalized_weights[component.name]
        for component in normalized_components
    )
    probabilities = [component.probability for component in normalized_components]
    dispersion = max(probabilities) - min(probabilities)
    warnings = [
        warning
        for component in normalized_components
        for warning in component.warnings
    ]
    if dispersion > disagreement_threshold:
        warnings.append("model_disagreement")

    return EnsembleProbabilityResult(
        probability=min(1.0, max(0.0, float(probability))),
        components=normalized_components,
        normalized_weights=normalized_weights,
        diagnostics={
            "component_count": len(normalized_components),
            "min_probability": min(probabilities),
            "max_probability": max(probabilities),
            "mean_probability": mean(probabilities),
            "dispersion": dispersion,
        },
        warnings=tuple(warnings),
    )
