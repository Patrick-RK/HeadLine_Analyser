import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors


def plot_moving_averages(df):
    """
    Plots the moving averages of the VADER sentiment scores along with the raw sentiment line.
    
    Args:
        df (DataFrame): A DataFrame containing sentiment analysis results and calculated moving averages.
    """
    # Set a professional plot style using seaborn
    sns.set(style="whitegrid")

    # Create a figure for the moving averages
    plt.figure(figsize=(12, 6))

    # Plot moving averages with clear and distinct styles
    plt.plot(df['Index'], df['VADER_MA_03'], label='VADER Compound (3% Moving Average)', color='red', linestyle='-', linewidth=2, alpha = 0.3)
    plt.plot(df['Index'], df['VADER_MA_10'], label='VADER Compound (10% Moving Average)', color='red', linestyle='-', linewidth=2, alpha = 0.6)
    
    # Plot the raw sentiment (scaled compound values)
    plt.plot(df['Index'], df['scaled_compound'], label='VADER Compound (Raw)', color='blue', linestyle='--', linewidth=2, alpha = 0.75)

    # Add title, labels, and grid
    plt.title('VADER Compound: Moving Averages and Raw Sentiment', fontsize=16, fontweight='bold')
    plt.xlabel('Headline Position (Index)', fontsize=12)
    plt.ylabel('Sentiment Scores', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()



# def plot_gradient_sentiment_line(df):
#     """
#     Plots a continuous line with gradient coloring based on VADER sentiment scores.
    
#     Args:
#         df (DataFrame): A DataFrame containing sentiment analysis results and scaled compound scores.
#     """
#     # Set a professional plot style using seaborn
#     sns.set(style="whitegrid")

#     # Create a figure for the sentiment line
#     plt.figure(figsize=(12, 6))

#     # Create a colormap that transitions from red (negative) to green (positive)
#     cmap = plt.get_cmap('RdYlGn')
#     norm = plt.Normalize(vmin=-1, vmax=1)

#     # Prepare the data for a gradient line
#     points = np.array([df['Index'], df['scaled_compound']]).T.reshape(-1, 1, 2)
#     segments = np.concatenate([points[:-1], points[1:]], axis=1)

#     # Create a LineCollection to handle gradient coloring
#     lc = LineCollection(segments, cmap=cmap, norm=norm)
#     lc.set_array(df['scaled_compound'])  # Set the color based on sentiment score
#     lc.set_linewidth(2)

#     # Add the LineCollection to the plot
#     plt.gca().add_collection(lc)

#     # Plot a color bar for reference
#     plt.colorbar(lc, label='Sentiment Score')

#     # Ensure the x-axis and y-axis limits match the data range
#     plt.xlim(df['Index'].min(), df['Index'].max())
#     plt.ylim(df['scaled_compound'].min() - 0.1, df['scaled_compound'].max() + 0.1)

#     # Scatter plot with color-coded dots for raw sentiment
#     plt.scatter(df['Index'], df['scaled_compound'], color=[cmap(norm(x)) for x in df['scaled_compound']], s=100, alpha=0.7)

#     # Add title, labels, and grid
#     plt.title('VADER Compound: Scaled Raw Sentiment Scores (Gradient Line)', fontsize=16, fontweight='bold')
#     plt.xlabel('Headline Position (Index)', fontsize=12)
#     plt.ylabel('Scaled Raw Sentiment Scores', fontsize=12)
#     plt.grid(True)

#     # Show the plot
#     plt.tight_layout()
#     plt.show()
