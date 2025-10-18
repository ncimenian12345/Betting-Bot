"""Data provider abstractions for odds and statistics."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Protocol, Sequence

import urllib.request

from .models import PlayerLine, PlayerStats


class OddsProvider(Protocol):
    """Protocol for classes that fetch player betting lines."""

    def fetch(self) -> Iterable[PlayerLine]:
        ...


class StatsProvider(Protocol):
    """Protocol for classes that fetch advanced player statistics."""

    def fetch(self) -> Iterable[PlayerStats]:
        ...


def _parse_player_lines(data: Sequence[dict]) -> List[PlayerLine]:
    results: List[PlayerLine] = []
    for item in data:
        results.append(
            PlayerLine(
                player_id=item["player_id"],
                player_name=item["player_name"],
                team=item["team"],
                market=item["market"],
                line_value=float(item["line_value"]),
                sportsbook=item["sportsbook"],
                odds=int(item["odds"]),
                last_updated=datetime.fromisoformat(item["last_updated"])
                if "last_updated" in item
                else datetime.utcnow(),
            )
        )
    return results


def _parse_player_stats(data: Sequence[dict]) -> List[PlayerStats]:
    results: List[PlayerStats] = []
    for item in data:
        results.append(
            PlayerStats(
                player_id=item["player_id"],
                player_name=item["player_name"],
                team=item["team"],
                stats={k: float(v) for k, v in item["stats"].items()},
                last_updated=datetime.fromisoformat(item["last_updated"])
                if "last_updated" in item
                else datetime.utcnow(),
            )
        )
    return results


class JsonFileOddsProvider:
    """Load betting lines from a JSON file."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def fetch(self) -> List[PlayerLine]:  # type: ignore[override]
        data = json.loads(self.path.read_text())
        return _parse_player_lines(data)


class JsonFileStatsProvider:
    """Load advanced player statistics from a JSON file."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def fetch(self) -> List[PlayerStats]:  # type: ignore[override]
        data = json.loads(self.path.read_text())
        return _parse_player_stats(data)


class HttpJsonOddsProvider:
    """Fetch betting lines from an HTTP endpoint returning JSON."""

    def __init__(self, url: str) -> None:
        self.url = url

    def fetch(self) -> List[PlayerLine]:  # type: ignore[override]
        with urllib.request.urlopen(self.url) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
        return _parse_player_lines(data)


class HttpJsonStatsProvider:
    """Fetch advanced stats from an HTTP endpoint returning JSON."""

    def __init__(self, url: str) -> None:
        self.url = url

    def fetch(self) -> List[PlayerStats]:  # type: ignore[override]
        with urllib.request.urlopen(self.url) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
        return _parse_player_stats(data)


def serialize_dataclasses(records: Iterable[PlayerLine | PlayerStats]) -> List[dict]:
    """Serialize dataclasses to dictionaries for debugging/logging."""

    from dataclasses import asdict

    return [asdict(record) for record in records]
