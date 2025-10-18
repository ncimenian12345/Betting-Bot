"""Utilities for updating betting lines and stats."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import PlayerLine, PlayerStats
from .providers import OddsProvider, StatsProvider
from .storage import BettingDataStore


@dataclass
class UpdateReport:
    """Summary of a data refresh."""

    lines_updated: int
    stats_updated: int


class BettingDataUpdater:
    """Fetch and persist player lines and stats."""

    def __init__(
        self,
        odds_provider: OddsProvider,
        stats_provider: StatsProvider,
        store: BettingDataStore,
    ) -> None:
        self.odds_provider = odds_provider
        self.stats_provider = stats_provider
        self.store = store

    # ------------------------------------------------------------------
    def update(self) -> UpdateReport:
        """Fetch fresh data and persist it to the store."""

        lines = list(self.odds_provider.fetch())
        stats = list(self.stats_provider.fetch())
        self.store.save_lines(lines)
        self.store.save_stats(stats)
        return UpdateReport(lines_updated=len(lines), stats_updated=len(stats))

    # ------------------------------------------------------------------
    @staticmethod
    def merge_lines_with_stats(
        lines: Sequence[PlayerLine], stats: Sequence[PlayerStats]
    ) -> dict[str, tuple[PlayerLine, PlayerStats]]:
        """Create a mapping of player id to (line, stats)."""

        stat_lookup = {player.player_id: player for player in stats}
        merged: dict[str, tuple[PlayerLine, PlayerStats]] = {}
        for line in lines:
            if line.player_id in stat_lookup:
                merged[line.player_id] = (line, stat_lookup[line.player_id])
        return merged


def ensure_iterable(records: Iterable[PlayerLine | PlayerStats]) -> list:
    """Materialize the iterable to a list (helper for tests/CLI)."""

    return list(records)
