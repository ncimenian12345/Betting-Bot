# NFL Betting Bot

This project provides a modular betting assistant that can refresh NFL player props, 
calculate advanced-stat-based confidence scores, and surface the top betting edges for the day.

## Features

- Update NFL player betting lines and advanced statistics from JSON sources (local files or HTTP endpoints).
- Persist the refreshed data locally for daily workflows.
- Combine player lines with advanced metrics to generate weighted confidence scores.
- Display the top betting opportunities along with a feature-by-feature confidence breakdown.
- Allow users to override the weighting of advanced statistics to fit their handicapping style.

## Getting Started

1. Install dependencies (Python 3.11+ recommended).
2. Refresh the local cache using the included sample data:

   ```bash
   python -m betting_bot update --lines betting_bot/data/sample_lines.json \
       --stats betting_bot/data/sample_stats.json
   ```

3. Display the top recommended bets:

   ```bash
   python -m betting_bot top-bets --limit 3
   ```

4. Override the confidence weights to emphasize different metrics:

   ```bash
   python -m betting_bot top-bets --weight usage_rate=0.5 --weight recent_form=0.3
   ```

The application stores cached data inside the `data/` directory by default. Use the
`--store` flag to change the location.

## Data Format

Both lines and stats commands expect JSON arrays. See `betting_bot/data/sample_lines.json`
and `betting_bot/data/sample_stats.json` for reference structures that can be adapted to
your own data pipelines or API integrations.

## Extending

Implement custom odds or stats providers by conforming to the `OddsProvider` and
`StatsProvider` protocols in `betting_bot/providers.py`. This allows integration with
public APIs or internal data sources while reusing the core scoring and recommendation
infrastructure.
