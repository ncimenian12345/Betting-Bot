"""Top bet selection logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Sequence

from .confidence import ConfidenceBreakdown, ConfidenceModel
from .models import PlayerLine, PlayerStats
from .updater import BettingDataUpdater


@dataclass
class BetRecommendation:
    """Container for a betting recommendation."""

    line: PlayerLine
    stats: PlayerStats
    confidence: ConfidenceBreakdown


class RecommendationEngine:
    """Generate bet recommendations using the confidence model."""

    def __init__(self, model: ConfidenceModel) -> None:
        self.model = model

    # ------------------------------------------------------------------
    def rank_bets(
        self,
        data: Mapping[str, tuple[PlayerLine, PlayerStats]],
        limit: int = 5,
    ) -> List[BetRecommendation]:
        """Rank bets by confidence and return the top results."""

        recommendations: List[BetRecommendation] = []
        for line, stats in data.values():
            breakdown = self.model.score(line, stats)
            recommendations.append(
                BetRecommendation(line=line, stats=stats, confidence=breakdown)
            )
        recommendations.sort(key=lambda rec: rec.confidence.confidence, reverse=True)
        return recommendations[:limit]

    # ------------------------------------------------------------------
    def top_from_store(
        self,
        updater: BettingDataUpdater,
        limit: int = 5,
    ) -> List[BetRecommendation]:
        """Load cached data and return top bets."""

        lines = updater.store.load_lines()
        stats = updater.store.load_stats()
        merged = BettingDataUpdater.merge_lines_with_stats(lines, stats)
        return self.rank_bets(merged, limit=limit)


def format_recommendations(recommendations: Iterable[BetRecommendation]) -> str:
    """Create a human readable summary of recommendations."""

    lines: List[str] = []
    for rec in recommendations:
        line = rec.line
        confidence_pct = rec.confidence.confidence * 100
        lines.append(
            (
                f"{line.player_name} ({line.team}) - {line.market} {line.line_value} "
                f"@ {line.sportsbook} (odds {line.odds:+d})\n"
                f"  Confidence: {confidence_pct:0.1f}%\n"
                f"  Feature breakdown: "
                + ", ".join(
                    f"{name}={value:0.2f}" for name, value in rec.confidence.feature_scores.items()
                )
            )
        )
    return "\n\n".join(lines)
