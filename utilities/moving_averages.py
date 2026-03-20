import pandas as pd


def calculate_moving_averages(df, window_percentages=None):
    """
    Calculates moving averages for compound sentiment scores.

    Uses the raw VADER compound score directly (already in [-1, 1])
    instead of rescaling with MinMaxScaler, so scores stay comparable
    across scrape runs.

    Args:
        df: DataFrame or list of dicts with a 'compound' column.
        window_percentages: List of window sizes as fractions of data length.

    Returns:
        DataFrame with scaled_compound and MA columns added.
    """
    if window_percentages is None:
        window_percentages = [0.05, 0.10, 0.20]

    if isinstance(df, list):
        df = pd.DataFrame(df)

    if 'compound' not in df.columns:
        raise ValueError("'compound' column not found in the DataFrame")

    df['Index'] = range(len(df))

    # Use raw compound directly — it is already [-1, 1]
    df['scaled_compound'] = df['compound']

    len_df = len(df)

    for pct in window_percentages:
        window = max(1, int(len_df * pct))
        col_name = f"MA_{int(pct * 100)}pct"
        df[col_name] = df['scaled_compound'].rolling(window=window).mean()

    return df
