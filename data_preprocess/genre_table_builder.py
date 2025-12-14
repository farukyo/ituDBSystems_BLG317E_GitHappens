# ==============================================================================
# genre_table_builder.py - Genre Table Builder
# ==============================================================================
# This script extracts unique genres from title.basics.csv file
# and creates a separate genre.csv file with genre_id.
# Generates a genre dimension table for database normalization.
# ==============================================================================

import os
import pandas as pd


def build_genre_df(
    title_basics_path: str | None = None,
    output_path: str | None = None,
) -> pd.DataFrame:
    """Read title.basics.csv, extract distinct genres, assign auto-increment ids.

    Parameters
    ----------
    title_basics_path : str | None
        Path to `title.basics.csv`. If None, resolves to `../data/title.basics.csv`.
    output_path : str | None
        Optional path to save the resulting DataFrame as CSV. If None, doesn't save.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: [genre_id, genre].
    """

    # Default paths relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if title_basics_path is None:
        title_basics_path = os.path.join(base_dir, "..", "data", "title.basics.csv")

    # Read only the genres column for efficiency
    df = pd.read_csv(title_basics_path, usecols=["genres"], dtype={"genres": "string"})

    # Split comma-separated genres, stack, drop duplicates and missing values
    genres_series = (
        df["genres"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
    )

    # Remove empty strings and special missing markers like "\\N"
    genres_series = genres_series[genres_series != ""]
    genres_series = genres_series[genres_series != "\\N"]

    unique_genres = genres_series.drop_duplicates().sort_values().reset_index(drop=True)

    genre_df = pd.DataFrame(
        {
            "genre_id": range(1, len(unique_genres) + 1),  # auto-increment starting from 1
            "genre": unique_genres,
        }
    )

    if output_path is not None:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        genre_df.to_csv(output_path, index=False)

    return genre_df


if __name__ == "__main__":
    # Convenience CLI: build genres and save next to original data file as genre.csv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_title_basics = os.path.join(base_dir, "..", "data", "title.basics.csv")
    default_output = os.path.join(base_dir, "..", "data", "genre.csv")

    df = build_genre_df(default_title_basics, default_output)
    print(df.head())
    print(f"Created {len(df)} distinct genres and saved to: {default_output}")

