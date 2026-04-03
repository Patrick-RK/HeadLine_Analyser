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
        mode='markers',
        name='Raw Sentiment',
        marker=dict(size=4, color='rgba(100,149,237,0.3)'),
        text=df['headline'],
        hovertemplate='<b>%{text}</b><br>Score: %{y:.2f}<extra></extra>',
    ))

    ma_styles = {
        'MA_5pct':  dict(color='rgba(150,150,150,0.4)', width=1, dash='dot'),
        'MA_10pct': dict(color='#c0392b', width=3),
        'MA_20pct': dict(color='#2c3e50', width=3),
    }
    ma_names = {'MA_5pct': '5% MA', 'MA_10pct': '10% MA', 'MA_20pct': '20% MA'}
    for col, style in ma_styles.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['Index'],
                y=df[col],
                mode='lines',
                name=ma_names[col],
                line=style,
            ))

    fig.update_layout(
        xaxis_title='Position (top of page →)',
        yaxis_title='Sentiment',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(t=40, b=40, l=50, r=10),
    )

    return fig.to_json()
