import plotly.graph_objects as go


def build_plotly_figure(df):
    """
    Build an interactive Plotly figure showing raw scaled sentiment
    and moving averages.

    Args:
        df: DataFrame with scaled_compound, Index, headline, and MA columns.

    Returns:
        Plotly figure as JSON-serialisable dict.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Index'],
        y=df['scaled_compound'],
        mode='lines+markers',
        name='Raw Sentiment',
        line=dict(color='royalblue', width=2),
        marker=dict(size=5),
        text=df['headline'],
        hovertemplate='<b>%{text}</b><br>Score: %{y:.2f}<extra></extra>',
    ))

    ma_colours = {'MA_5pct': 'navy', 'MA_10pct': 'crimson', 'MA_20pct': 'darkorange'}
    for col, colour in ma_colours.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Index'],
                y=df[col],
                mode='lines',
                name=col.replace('_', ' '),
                line=dict(color=colour, width=2, dash='dash'),
                opacity=0.7,
            ))

    fig.update_layout(
        title='VADER Compound: Moving Averages and Raw Sentiment',
        xaxis_title='Headline Position (Index)',
        yaxis_title='Scaled Sentiment Score',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(t=80, b=40, l=60, r=20),
    )

    return fig.to_json()
