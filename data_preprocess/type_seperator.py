import os
import pandas as pd


MOVIE_TYPES = {"movie", "short", "tvMovie", "video"}
SERIES_TYPES = {
    "tvSeries",
    "tvMiniSeries",
    "tvEpisode",
    "tvPilot",
    "tvShort",
    "tvSpecial",
}


def get_distinct_title_types(title_basics_path: str | None = None) -> pd.Series:
    """Read title.basics.csv and return distinct titleType values.

    Parameters
    ----------
    title_basics_path : str | None
        Path to `title.basics.csv`. If None, resolves to `../data/title.basics.csv`.

    Returns
    -------
    pd.Series
        Sorted distinct titleType values.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if title_basics_path is None:
        title_basics_path = os.path.join(base_dir, "..", "data", "title.basics.csv")

    # Read only the titleType column
    df = pd.read_csv(title_basics_path, usecols=["titleType"], dtype={"titleType": "string"})

    title_types = df["titleType"].dropna().str.strip()

    # Remove empty strings and any placeholder like "\\N"
    title_types = title_types[title_types != ""]
    title_types = title_types[title_types != "\\N"]

    distinct_types = title_types.drop_duplicates().sort_values().reset_index(drop=True)
    return distinct_types


def split_titles_by_type(
    title_basics_path: str | None = None,
    movies_output_path: str | None = None,
    series_output_path: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split title.basics.csv into movies and series CSVs.

    Movies are rows where titleType is in MOVIE_TYPES.
    Series are rows where titleType is in SERIES_TYPES.
    Rows with titleType outside these sets (e.g., videoGame) are ignored.

    Parameters
    ----------
    title_basics_path : str | None
        Path to `title.basics.csv`. If None, resolves to `../data/title.basics.csv`.
    movies_output_path : str | None
        Path to save movies CSV. If None, defaults to `../data/movies.basics.csv`.
    series_output_path : str | None
        Path to save series CSV. If None, defaults to `../data/series.basics.csv`.

    Returns
    -------
    (movies_df, series_df) : tuple[pd.DataFrame, pd.DataFrame]
        DataFrames for movies and series.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if title_basics_path is None:
        title_basics_path = os.path.join(base_dir, "..", "data", "title.basics.csv")

    if movies_output_path is None:
        movies_output_path = os.path.join(base_dir, "..", "data", "movies.basics.csv")
    if series_output_path is None:
        series_output_path = os.path.join(base_dir, "..", "data", "series.basics.csv")

    # Read the full title.basics.csv
    df = pd.read_csv(title_basics_path)

    # Normalize titleType for safety
    df["titleType"] = df["titleType"].astype("string").str.strip()

    movies_df = df[df["titleType"].isin(MOVIE_TYPES)].copy()
    series_df = df[df["titleType"].isin(SERIES_TYPES)].copy()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(movies_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(series_output_path), exist_ok=True)

    movies_df.to_csv(movies_output_path, index=False)
    series_df.to_csv(series_output_path, index=False)

    return movies_df, series_df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_title_basics = os.path.join(base_dir, "..", "data", "title.basics.csv")

    # 1) Show distinct title types (for info/debug)
    distinct_types = get_distinct_title_types(default_title_basics)
    print("Distinct titleType values in title.basics.csv:\n")
    for i, t in enumerate(distinct_types, start=1):
        print(f"{i:2d}. {t}")
    print(f"\nTotal distinct titleType values: {len(distinct_types)}\n")

    # 2) Split into movies and series CSVs
    movies_path = os.path.join(base_dir, "..", "data", "movies.basics.csv")
    series_path = os.path.join(base_dir, "..", "data", "series.basics.csv")

    movies_df, series_df = split_titles_by_type(
        title_basics_path=default_title_basics,
        movies_output_path=movies_path,
        series_output_path=series_path,
    )

    print("Split completed:")
    print(f"  Movies rows : {len(movies_df):,} -> {movies_path}")
    print(f"  Series rows : {len(series_df):,} -> {series_path}")
