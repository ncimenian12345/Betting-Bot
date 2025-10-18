"""Command line entry-point for the NFL betting bot."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from .confidence import ConfidenceModel
from .providers import JsonFileOddsProvider, JsonFileStatsProvider
from .recommendations import RecommendationEngine, format_recommendations
from .storage import BettingDataStore
from .updater import BettingDataUpdater


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NFL betting bot utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update", help="Refresh betting lines and stats")
    update.add_argument("--lines", required=True, help="Path to lines JSON file")
    update.add_argument("--stats", required=True, help="Path to stats JSON file")
    update.add_argument(
        "--store",
        default="data",
        help="Directory where cached data should be stored",
    )

    top = subparsers.add_parser("top-bets", help="Display the top betting edges")
    top.add_argument("--store", default="data", help="Data directory")
    top.add_argument("--limit", type=int, default=5, help="Number of bets to display")
    top.add_argument(
        "--weight",
        action="append",
        default=[],
        help=(
            "Override confidence weight; use KEY=VALUE (e.g. --weight usage_rate=0.4)."
            " Available keys: projection_diff, usage_rate, matchup_adjustment,"
            " recent_form, injury_safety"
        ),
    )

    return parser


def parse_weights(values: list[str]) -> Dict[str, float]:
    overrides: Dict[str, float] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid weight override: {value}")
        key, raw = value.split("=", 1)
        try:
            overrides[key] = float(raw)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid float for weight {key}: {raw}") from exc
    return overrides


def cmd_update(args: argparse.Namespace) -> None:
    store = BettingDataStore(Path(args.store))
    odds_provider = JsonFileOddsProvider(args.lines)
    stats_provider = JsonFileStatsProvider(args.stats)
    updater = BettingDataUpdater(odds_provider, stats_provider, store)
    report = updater.update()
    print(
        "Update complete: "
        f"{report.lines_updated} lines and {report.stats_updated} stat profiles saved."
    )


def cmd_top_bets(args: argparse.Namespace) -> None:
    store = BettingDataStore(Path(args.store))
    overrides = parse_weights(args.weight)
    model = ConfidenceModel(weights=overrides or None)
    odds_provider = JsonFileOddsProvider(store.root / "player_lines.json")
    stats_provider = JsonFileStatsProvider(store.root / "player_stats.json")
    updater = BettingDataUpdater(odds_provider, stats_provider, store)
    engine = RecommendationEngine(model)
    recommendations = engine.top_from_store(updater, limit=args.limit)
    if not recommendations:
        print("No betting data available. Run the update command first.")
        return
    print(format_recommendations(recommendations))


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "update":
        cmd_update(args)
    elif args.command == "top-bets":
        cmd_top_bets(args)
    else:  # pragma: no cover - future-proof fallback
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
