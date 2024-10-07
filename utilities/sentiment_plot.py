import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_sentiment_analysis(data: list):
    """
    Plots the comparison of VADER sentiment scores directly from a list of sentiment analysis results.

    Args:
        data (list): A list of dictionaries containing sentiment analysis results.
    """
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data)
    
    # Create an index for the x-axis representing the position of the headline from the top of the page
    df['Index'] = range(len(df))

    # Calculate moving averages based on percentages of the length of headlines
    len_df = len(df)
    df['VADER_MA_10'] = df['compound'].rolling(window=int(len_df * 0.03)).mean()
    df['VADER_MA_25'] = df['compound'].rolling(window=int(len_df * 0.10)).mean()
    df['VADER_MA_33'] = df['compound'].rolling(window=int(len_df * 0.20)).mean()

    # Set a professional plot style using seaborn
    sns.set(style="whitegrid")

    # Define the colors for moving averages and raw sentiment (positive green, negative red)
    df['color'] = df['compound'].apply(lambda x: 'darkgreen' if x > 0.5 else
                                                'lightgreen' if x > 0 else
                                                'lightcoral' if x > -0.5 else 'darkred')

    # Create a figure for visualizing the comparison
    plt.figure(figsize=(12, 8))

    # Plot the moving averages (10%, 25%, 33%) and raw VADER sentiment scores
    plt.subplot(2, 1, 1)
    
    # Plot moving averages with shades of grey
    plt.plot(df['Index'], df['VADER_MA_10'], label='VADER Compound (10% Moving Average)', color='lightgrey',linestyle=':', linewidth=2)
    plt.plot(df['Index'], df['VADER_MA_25'], label='VADER Compound (25% Moving Average)', color='darkgrey', linestyle='-',  linewidth=2)
    plt.plot(df['Index'], df['VADER_MA_33'], label='VADER Compound (33% Moving Average)', color='black', linestyle='--', linewidth=2)

    # Plot raw sentiment as a line graph
    plt.plot(df['Index'], df['compound'], label='VADER Compound (Raw)', color='green', marker='o', alpha=0.6)
    
    # Scatter raw sentiment with different colors on top of the line
    plt.scatter(df['Index'], df['compound'], color=df['color'], label='VADER Compound (Raw)', alpha=0.6)

    plt.title('VADER Compound Moving Averages & Raw Sentiment', fontsize=14, fontweight='bold')
    plt.xlabel('Headline Position (Index)')
    plt.ylabel('Sentiment Scores')
    plt.legend()
    plt.grid(True)

    # Plot the raw sentiment with a line graph (second plot)
    plt.subplot(2, 1, 2)
    
    # Line plot for raw sentiment with red for negative and green for positive
    plt.plot(df['Index'], df['compound'], color='green', marker='o', alpha=0.6, label='VADER Compound Score')

    plt.title('VADER Compound Raw Sentiment Scores', fontsize=14, fontweight='bold')
    plt.xlabel('Headline Position (Index)')
    plt.ylabel('Raw Sentiment Scores')
    plt.grid(True)

    # Show the plots
    plt.tight_layout()
    plt.show()
