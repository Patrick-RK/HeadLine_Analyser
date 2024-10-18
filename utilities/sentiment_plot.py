import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import textwrap

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
    plt.plot(df['Index'], df['VADER_MA_03'], label='VADER Compound (5% Moving Average)', color='navy', linestyle='--', linewidth=2, alpha=0.3)
    # plt.plot(df['Index'], df['VADER_MA_10'], label='VADER Compound (10% Moving Average)', color='red', linestyle='-', linewidth=2, alpha=0.6)
    
    # Plot the raw sentiment (scaled compound values)
    plt.plot(df['Index'], df['scaled_compound'], label='VADER Compound (Raw)', color='blue', linestyle='solid', linewidth=2, alpha=0.75)

    # Add title, labels, and grid
    plt.title('VADER Compound: Moving Averages and Raw Sentiment', fontsize=16, fontweight='bold', pad=40)
    plt.xlabel('headers Position (Index)', fontsize=12)
    plt.ylabel('Sentiment Scores', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True)

    # Return the current plot object (figure)
    return plt

def add_annotations(df, plt, num_annotations=3):
    """
    Adds circles and annotations to the plot for the top 'num_annotations' most positive and bottom 'num_annotations' most negative points.
    The annotation appears above the dot for positive values and below for negative values, centered horizontally.
    
    Args:
        df (DataFrame): A DataFrame containing sentiment analysis results.
        plt (matplotlib.pyplot): The plot object to which annotations are added.
        num_annotations (int): The number of positive and negative points to annotate (default is 1).
    """
    # Prepare data, excluding NaN values
    y_values = df['scaled_compound']
    x_values = df['Index']
    headlines = df['headline']

    # Remove NaN values
    valid_mask = y_values.notna()
    y_values_valid = y_values[valid_mask].reset_index(drop=True)
    x_values_valid = x_values[valid_mask].reset_index(drop=True)
    headlines_valid = headlines[valid_mask].reset_index(drop=True)

    # Sort sentiment values for top 'num_annotations' most positive and bottom 'num_annotations' most negative
    top_indices = y_values_valid.nlargest(num_annotations).index  # Top most positive values
    bottom_indices = y_values_valid.nsmallest(num_annotations).index  # Bottom most negative values

    # Plot circles and add annotations for the top most positive points
    for idx in top_indices:
    # Wrap the text at a certain width (e.g., 20 characters)
        wrapped_text = '\n'.join(textwrap.wrap(f'{headlines_valid.iloc[idx]}', width=20))
        
        text_length = len(wrapped_text)

        # Set a base offset and adjust it based on text length (experiment with the factor to find the best value)
        vertical_offset = 15 + (text_length // 10) * 1.25  # Adjust factor as needed

        # Annotate above the dot with dynamic vertical offset
        plt.annotate(wrapped_text,
                    (x_values_valid.iloc[idx], y_values_valid.iloc[idx]),
                    textcoords="offset points",
                    xytext=(0, vertical_offset),  # Dynamic vertical offset
                    ha='center',  # Center horizontally
                    va='bottom',  # Text goes above the dot
                    fontsize=8, fontweight='bold', color='green')

        plt.plot(x_values_valid.iloc[idx], y_values_valid.iloc[idx], 'o', markersize=10, markeredgewidth=2, markeredgecolor='black', markerfacecolor='green', zorder=5, alpha=0.8)  # Circle the point


    # Plot circles and add annotations for the bottom most negative points
    for idx in bottom_indices:
        wrapped_text = '\n'.join(textwrap.wrap(f'{headlines_valid.iloc[idx]}', width=20))
        
        # Calculate the dynamic vertical offset based on text length
        text_length = len(wrapped_text)
        vertical_offset = -15 - (text_length // 10) * 5 # Adjust factor as needed for negative offset

        # Plot the point
        plt.plot(x_values_valid.iloc[idx], y_values_valid.iloc[idx], 'o', markersize=10, 
                markeredgewidth=2, markeredgecolor='black', markerfacecolor='red', 
                zorder=5, alpha=0.8)  # Circle the point

        # Annotate below the dot with dynamic vertical offset
        plt.annotate(wrapped_text,
                    (x_values_valid.iloc[idx], y_values_valid.iloc[idx]),
                    textcoords="offset points",
                    xytext=(0, vertical_offset),  # Dynamic negative vertical offset
                    ha='center',  
                    va='bottom',  # Text goes below the dot
                    fontsize=8, fontweight='bold', color='red')
        # Show the plot with the annotations
        plt.tight_layout()
    plt.show()

def create_plot(df):
    ma_plt = plot_moving_averages(df)
    annotated_plot = add_annotations(df, ma_plt)

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
#     plt.xlabel('headers Position (Index)', fontsize=12)
#     plt.ylabel('Scaled Raw Sentiment Scores', fontsize=12)
#     plt.grid(True)

#     # Show the plot
#     plt.tight_layout()
#     plt.show()
