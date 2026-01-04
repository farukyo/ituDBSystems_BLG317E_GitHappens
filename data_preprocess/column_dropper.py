# ==============================================================================
# column_dropper.py - Unnecessary Column Remover Script
# ==============================================================================
# This script removes unnecessary columns from movies and series CSV files.
# - From both files: originalTitle column
# - From movies only: endYear column (meaningless for movies)
# Used to simplify the database schema.
# ==============================================================================

import os
import pandas as pd


def _default_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    movies_path = os.path.join(base_dir, "..", "data", "movies.basics.csv")
    series_path = os.path.join(base_dir, "..", "data", "series.basics.csv")
    return movies_path, series_path


def drop_unwanted_columns(
    movies_path: str | None = None,
    series_path: str | None = None,
    movies_output_path: str | None = None,
    series_output_path: str | None = None,
):
    """Drop specified columns from movies/series basics CSVs.

    Requirements:
    - From both movies and series basics, drop `originalTitle`.
    - Additionally, from movies basics, drop `endYear`.
    - Overwrite the same files by default.
    """

    default_movies, default_series = _default_paths()
    if movies_path is None:
        movies_path = default_movies
    if series_path is None:
        series_path = default_series

    if movies_output_path is None:
        movies_output_path = movies_path
    if series_output_path is None:
        series_output_path = series_path

    # Load CSVs
    movies_df = pd.read_csv(movies_path)
    series_df = pd.read_csv(series_path)

    # Drop columns if they exist
    movies_drop_cols = [
        col for col in ["originalTitle", "endYear"] if col in movies_df.columns
    ]
    series_drop_cols = [col for col in ["originalTitle"] if col in series_df.columns]

    movies_df = movies_df.drop(columns=movies_drop_cols)
    series_df = series_df.drop(columns=series_drop_cols)

    # Ensure output dirs exist
    os.makedirs(os.path.dirname(movies_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(series_output_path), exist_ok=True)

    # Save back
    movies_df.to_csv(movies_output_path, index=False)
    series_df.to_csv(series_output_path, index=False)

    return {
        "movies_path": movies_output_path,
        "series_path": series_output_path,
        "movies_columns": list(movies_df.columns),
        "series_columns": list(series_df.columns),
    }


if __name__ == "__main__":
    movies_path, series_path = _default_paths()

    result = drop_unwanted_columns(movies_path, series_path)

    print("Table fix completed:")
    print(f"  Movies file : {result['movies_path']}")
    print(f"    Columns   : {', '.join(result['movies_columns'])}")
    print(f"  Series file : {result['series_path']}")
    print(f"    Columns   : {', '.join(result['series_columns'])}")
