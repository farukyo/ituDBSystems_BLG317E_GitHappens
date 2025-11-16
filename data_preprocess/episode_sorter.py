from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EPISODES_FILE = DATA_DIR / "episodes.basics.csv"


def coerce_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype="string",
        na_values=["\\N", ""],
        keep_default_na=False,
        header=None,
    )


def detect_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] >= 10:
        columns = [
            "tconst",
            "titleType",
            "primaryTitle",
            "isAdult",
            "startYear",
            "endYear",
            "runtimeMinutes",
            "genres",
            "parentTconst",
            "seasonNumber",
            "episodeNumber",
        ][: df.shape[1]]
        df.columns = columns
    return df


def sort_episodes(df: pd.DataFrame) -> pd.DataFrame:
    sort_columns = ["parentTconst", "seasonNumber", "episodeNumber"]
    for column in sort_columns[1:]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.sort_values(sort_columns, na_position="last").reset_index(drop=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, na_rep="\\N")


def run(input_path: Path, output_path: Path) -> None:
    df = load_csv(input_path)
    df = detect_columns(df)
    sorted_df = sort_episodes(df)
    write_csv(sorted_df, output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sort episodes.basics.csv by parent series"
    )
    parser.add_argument(
        "--input",
        type=coerce_path,
        default=EPISODES_FILE,
        help=f"Path to episodes CSV (default: {EPISODES_FILE})",
    )
    parser.add_argument(
        "--output",
        type=coerce_path,
        default=EPISODES_FILE,
        help="Path to write sorted CSV (default: overwrite input)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()

