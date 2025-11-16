from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SERIES_FILE = DATA_DIR / "series.basics.csv"
EPISODE_LOOKUP_FILE = DATA_DIR / "title.episode.csv"
OUTPUT_EPISODES_FILE = DATA_DIR / "episodes.basics.csv"


def coerce_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype="string",
        na_values=["\\N", ""],
        keep_default_na=False,
    )


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, na_rep="\\N")


def extract_episodes(series_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    episode_mask = series_df["titleType"].eq("tvEpisode")
    episodes_df = series_df.loc[episode_mask].copy().reset_index(drop=True)
    remaining_series_df = series_df.loc[~episode_mask].copy().reset_index(drop=True)
    return remaining_series_df, episodes_df


def enrich_with_episode_numbers(
    episodes_df: pd.DataFrame,
    episode_lookup_df: pd.DataFrame,
) -> pd.DataFrame:
    lookup_df = episode_lookup_df.rename(
        columns={"tconst": "tconst", "parentTconst": "parentTconst"}
    )
    merged_df = episodes_df.merge(lookup_df, on="tconst", how="left")
    merged_df.rename(
        columns={
            "parentTconst": "parentTconst",
            "seasonNumber": "seasonNumber",
            "episodeNumber": "episodeNumber",
        },
        inplace=True,
    )
    merged_df["seasonNumber"] = pd.to_numeric(merged_df["seasonNumber"], errors="coerce")
    merged_df["episodeNumber"] = pd.to_numeric(
        merged_df["episodeNumber"], errors="coerce"
    )
    return merged_df


def verify_counts(original: pd.DataFrame, cleaned: pd.DataFrame, episodes: pd.DataFrame) -> None:
    if len(original) != len(cleaned) + len(episodes):
        raise ValueError(
            "Row count mismatch: original={}, cleaned={}, episodes={}".format(
                len(original), len(cleaned), len(episodes)
            )
        )


def run(
    series_file: Path,
    episode_lookup_file: Path,
    output_series_file: Path,
    output_episodes_file: Path,
) -> None:
    series_df = load_csv(series_file)
    episode_lookup_df = load_csv(episode_lookup_file)

    cleaned_series_df, episodes_df = extract_episodes(series_df)
    enriched_episodes_df = enrich_with_episode_numbers(episodes_df, episode_lookup_df)

    verify_counts(series_df, cleaned_series_df, episodes_df)

    write_csv(cleaned_series_df, output_series_file)
    write_csv(enriched_episodes_df, output_episodes_file)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract episodes from series CSV")
    parser.add_argument(
        "--series",
        type=coerce_path,
        default=SERIES_FILE,
        help=f"Path to series.basics.csv (default: {SERIES_FILE})",
    )
    parser.add_argument(
        "--episode-lookup",
        type=coerce_path,
        default=EPISODE_LOOKUP_FILE,
        help=f"Path to title.episode.csv (default: {EPISODE_LOOKUP_FILE})",
    )
    parser.add_argument(
        "--output-series",
        type=coerce_path,
        default=SERIES_FILE,
        help="Where to write the cleaned series file (default: overwrite input)",
    )
    parser.add_argument(
        "--output-episodes",
        type=coerce_path,
        default=OUTPUT_EPISODES_FILE,
        help=f"Where to write the new episodes CSV (default: {OUTPUT_EPISODES_FILE})",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run(
        series_file=args.series,
        episode_lookup_file=args.episode_lookup,
        output_series_file=args.output_series,
        output_episodes_file=args.output_episodes,
    )


if __name__ == "__main__":
    main()

