"""Data models for the betting bot."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class PlayerLine:
    """Represents a single betting line for a player."""

    player_id: str
    player_name: str
    team: str
    market: str
    line_value: float
    sportsbook: str
    odds: int
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlayerStats:
    """Container for advanced player statistics."""

    player_id: str
    player_name: str
    team: str
    stats: Dict[str, float]
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def get(self, stat: str, default: float = 0.0) -> float:
        """Return a stat by name with a default."""

        return self.stats.get(stat, default)
