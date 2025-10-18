"""Confidence scoring for betting recommendations."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping

from .models import PlayerLine, PlayerStats


DEFAULT_WEIGHTS: Dict[str, float] = {
    "projection_diff": 0.35,
    "usage_rate": 0.25,
    "matchup_adjustment": 0.2,
    "recent_form": 0.15,
    "injury_safety": 0.05,
}


@dataclass
class ConfidenceBreakdown:
    """Detailed scoring for a single recommendation."""

    raw_score: float
    confidence: float
    feature_scores: Dict[str, float]


class ConfidenceModel:
    """Compute confidence scores using weighted advanced stats."""

    def __init__(self, weights: Mapping[str, float] | None = None) -> None:
        self.weights: Dict[str, float] = dict(DEFAULT_WEIGHTS)
        if weights:
            self.weights.update(weights)
        total = sum(self.weights.values())
        if total == 0:
            raise ValueError("At least one weight must be non-zero")
        # Normalize to ensure a weighted average
        self.weights = {key: value / total for key, value in self.weights.items()}

    # ------------------------------------------------------------------
    def score(self, line: PlayerLine, stats: PlayerStats) -> ConfidenceBreakdown:
        """Return a confidence score in the range [0, 1]."""

        feature_scores: Dict[str, float] = {
            "projection_diff": self._projection_diff(line, stats),
            "usage_rate": stats.get("usage_rate", 0.0) / 100.0,
            "matchup_adjustment": self._matchup_adjustment(stats),
            "recent_form": stats.get("recent_form", 0.5),
            "injury_safety": 1.0 - stats.get("injury_risk", 0.0),
        }
        raw = sum(feature_scores[key] * self.weights.get(key, 0.0) for key in feature_scores)
        confidence = self._squash(raw)
        return ConfidenceBreakdown(raw_score=raw, confidence=confidence, feature_scores=feature_scores)

    # ------------------------------------------------------------------
    @staticmethod
    def _projection_diff(line: PlayerLine, stats: PlayerStats) -> float:
        projection = stats.get("projected_value", line.line_value)
        # normalized difference: >0 if projection above line (favorable for overs)
        diff = projection - line.line_value
        # assume typical lines within +/- 20 units (yards/receptions etc.)
        normalized = max(min(diff / 20.0 + 0.5, 1.0), 0.0)
        return normalized

    # ------------------------------------------------------------------
    @staticmethod
    def _matchup_adjustment(stats: PlayerStats) -> float:
        defense_rank = stats.get("opponent_pass_rank", 16.0)
        # Convert ranking (1 best defense) into scale where 0=hard matchup,1=easier
        return max(min(1.0 - (defense_rank - 1) / 31.0, 1.0), 0.0)

    # ------------------------------------------------------------------
    @staticmethod
    def _squash(value: float) -> float:
        """Smoothly squash values into [0, 1] using a logistic curve."""

        return 1.0 / (1.0 + math.exp(-6 * (value - 0.5)))
