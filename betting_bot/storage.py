"""Simple storage utilities for caching betting data locally."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .models import PlayerLine, PlayerStats


class BettingDataStore:
    """Persist betting data to disk as JSON."""

    def __init__(self, root: Path | str = "data") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lines_path = self.root / "player_lines.json"
        self._stats_path = self.root / "player_stats.json"

    # ------------------------------------------------------------------
    def save_lines(self, lines: Iterable[PlayerLine]) -> None:
        """Persist player betting lines."""

        payload: List[dict] = []
        for line in lines:
            payload.append(
                {
                    "player_id": line.player_id,
                    "player_name": line.player_name,
                    "team": line.team,
                    "market": line.market,
                    "line_value": line.line_value,
                    "sportsbook": line.sportsbook,
                    "odds": line.odds,
                    "last_updated": line.last_updated.isoformat(),
                }
            )
        self._lines_path.write_text(json.dumps(payload, indent=2))

    # ------------------------------------------------------------------
    def save_stats(self, stats: Iterable[PlayerStats]) -> None:
        """Persist player statistics."""

        payload: List[dict] = []
        for player in stats:
            payload.append(
                {
                    "player_id": player.player_id,
                    "player_name": player.player_name,
                    "team": player.team,
                    "stats": player.stats,
                    "last_updated": player.last_updated.isoformat(),
                }
            )
        self._stats_path.write_text(json.dumps(payload, indent=2))

    # ------------------------------------------------------------------
    def load_lines(self) -> List[PlayerLine]:
        """Load cached player lines."""

        if not self._lines_path.exists():
            return []
        data = json.loads(self._lines_path.read_text())
        return [
            PlayerLine(
                player_id=item["player_id"],
                player_name=item["player_name"],
                team=item["team"],
                market=item["market"],
                line_value=float(item["line_value"]),
                sportsbook=item["sportsbook"],
                odds=int(item["odds"]),
                last_updated=datetime.fromisoformat(item["last_updated"]),
            )
            for item in data
        ]

    # ------------------------------------------------------------------
    def load_stats(self) -> List[PlayerStats]:
        """Load cached player stats."""

        if not self._stats_path.exists():
            return []
        data = json.loads(self._stats_path.read_text())
        return [
            PlayerStats(
                player_id=item["player_id"],
                player_name=item["player_name"],
                team=item["team"],
                stats={k: float(v) for k, v in item["stats"].items()},
                last_updated=datetime.fromisoformat(item["last_updated"]),
            )
            for item in data
        ]
