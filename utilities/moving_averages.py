import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def calculate_moving_averages(df, window_percentages=[0.03, 0.10, 0.20]):
    """
    Calculates scaled moving averages for the sentiment scores based on the provided window percentages.
    
    Args:
        df (DataFrame or list): The DataFrame containing sentiment analysis results. If a list is passed, it will be converted to a DataFrame.
        window_percentages (list): List of window sizes as percentages of the data length.
    
    Returns:
        DataFrame: Updated DataFrame with scaled moving averages columns.
    """
    # Convert to DataFrame if it's a list of dictionaries
    if isinstance(df, list):
        df = pd.DataFrame(df)

    # Ensure that the 'compound' column exists before scaling
    if 'compound' not in df.columns:
        raise ValueError("'compound' column not found in the DataFrame")

    # Add an 'Index' column for plotting (if it doesn't exist)
    df['Index'] = range(len(df))

    # Apply MinMax scaling to the compound scores
    scaler = MinMaxScaler(feature_range=(-1, 1))
    df['scaled_compound'] = scaler.fit_transform(df[['compound']])

    # Calculate the length of the DataFrame
    len_df = len(df)

    # Calculate moving averages for the provided window percentages on the scaled compound values
    df['VADER_MA_03'] = df['scaled_compound'].rolling(window=int(len_df * window_percentages[0])).mean()
    df['VADER_MA_10'] = df['scaled_compound'].rolling(window=int(len_df * window_percentages[1])).mean()
    df['VADER_MA_20'] = df['scaled_compound'].rolling(window=int(len_df * window_percentages[2])).mean()

    return df
