import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_pattern_chart(stock_data, pattern_data):
    """
    Creates a plotly figure for visualizing a detected pattern
    """
    pattern_type = pattern_data['pattern']

    # Extract the window of interest
    if 'window_start' in pattern_data and 'window_end' in pattern_data:
        window_start = pattern_data['window_start']
        window_end = pattern_data['window_end']
        window_data = stock_data.iloc[window_start:window_end]
    else:
        start_date = pd.to_datetime(pattern_data['start_date'])
        end_date = pd.to_datetime(pattern_data['end_date'])
        window_data = stock_data[(stock_data['Date'] >= start_date) & (stock_data['Date'] <= end_date)]

    # Add some buffer before and after the pattern for context
    buffer_length = max(20, int(len(window_data) * 0.2))
    start_idx = max(0, window_start - buffer_length) if 'window_start' in pattern_data else 0
    end_idx = min(len(stock_data), window_end + buffer_length) if 'window_end' in pattern_data else len(stock_data)
    extended_data = stock_data.iloc[start_idx:end_idx]

    # Create the main candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=window_data['Date'],
        open=window_data['Price_Open'],
        high=window_data['Price_High'],
        low=window_data['Price_Low'],
        close=window_data['Price_Close'],
        name='Price'
    )])

    # Add volume as a bar chart at the bottom
    if 'Price_Volume' in extended_data.columns:
        fig.add_trace(go.Bar(
            x=extended_data['Date'],
            y=extended_data['Price_Volume'],
            name='Volume',
            marker_color='rgba(128, 128, 128, 0.5)',
            opacity=0.5,
            yaxis='y2'
        ))
    else:
        raise ValueError("Missing required column: 'Price_Volume'")

    # Add moving averages
    if 'MA20' in extended_data.columns:
        fig.add_trace(go.Scatter(
            x=extended_data['Date'],
            y=extended_data['MA20'],
            mode='lines',
            name='20-Day MA',
            line=dict(color='rgba(255, 165, 0, 0.8)', width=1)
        ))

    if 'MA50' in extended_data.columns:
        fig.add_trace(go.Scatter(
            x=extended_data['Date'],
            y=extended_data['MA50'],
            mode='lines',
            name='50-Day MA',
            line=dict(color='rgba(255, 0, 255, 0.8)', width=1)
        ))

    # Add support and resistance lines
    if 'support' in pattern_data and pattern_data['support'] is not None:
        support = pattern_data['support']
        fig.add_shape(
            type="line",
            x0=extended_data['Date'].iloc[0],
            y0=support,
            x1=extended_data['Date'].iloc[-1],
            y1=support,
            line=dict(
                color='green',
                width=2,
                dash='dash',
            ),
            name='Support'
        )

        # Add support level annotation
        fig.add_annotation(
            x=extended_data['Date'].iloc[-1],
            y=support,
            text=f"Support: {support:.2f}",
            showarrow=False,
            yshift=10,
            font=dict(color='green')
        )

    if 'resistance' in pattern_data and pattern_data['resistance'] is not None:
        resistance = pattern_data['resistance']
        fig.add_shape(
            type="line",
            x0=extended_data['Date'].iloc[0],
            y0=resistance,
            x1=extended_data['Date'].iloc[-1],
            y1=resistance,
            line=dict(
                color='red',
                width=2,
                dash='dash',
            ),
            name='Resistance'
        )

        # Add resistance level annotation
        fig.add_annotation(
            x=extended_data['Date'].iloc[-1],
            y=resistance,
            text=f"Resistance: {resistance:.2f}",
            showarrow=False,
            yshift=-10,
            font=dict(color='red')
        )

    # Add trend lines for corridor, rectangle, and triangle patterns
    if pattern_type in ['ascending_corridor', 'descending_corridor', 'neutral_rectangle', 'diverging_rectangle', 'ascending_triangle']:
        if 'high_line' in pattern_data and 'low_line' in pattern_data:
            # Extract pattern time window
            pattern_dates = window_data['Date']
            high_line = pattern_data['high_line']
            low_line = pattern_data['low_line']

            # Upper trend line
            fig.add_trace(go.Scatter(
                x=pattern_dates,
                y=high_line,
                mode='lines',
                name='Upper Trend',
                line=dict(color='rgba(255, 0, 0, 0.8)', width=2, dash='dash')
            ))

            # Lower trend line
            fig.add_trace(go.Scatter(
                x=pattern_dates,
                y=low_line,
                mode='lines',
                name='Lower Trend',
                line=dict(color='rgba(0, 255, 0, 0.8)', width=2, dash='dash')
            ))

    # Highlight specific features for patterns with peaks/troughs
    if 'peaks' in pattern_data and len(pattern_data['peaks']) > 0:
        # Add peak markers
        peak_indices = pattern_data['peaks']
        if isinstance(peak_indices, (list, np.ndarray)) and len(peak_indices) > 0:
            peak_dates = [window_data['Date'].iloc[i] for i in peak_indices if i < len(window_data)]
            peak_values = [window_data['Price_Close'].iloc[i] for i in peak_indices if i < len(window_data)]

            fig.add_trace(go.Scatter(
                x=peak_dates,
                y=peak_values,
                mode='markers',
                marker=dict(
                    size=10,
                    color='red',
                    symbol='circle',
                    line=dict(width=2, color='red')
                ),
                name='Peaks'
            ))

    if 'troughs' in pattern_data and len(pattern_data['troughs']) > 0:
        trough_indices = pattern_data['troughs']
        if isinstance(trough_indices, (list, np.ndarray)) and len(trough_indices) > 0:
            trough_dates = [window_data['Date'].iloc[i] for i in trough_indices if i < len(window_data)]
            trough_values = [window_data['Price_Close'].iloc[i] for i in trough_indices if i < len(window_data)]
            fig.add_trace(go.Scatter(
                x=trough_dates,
                y=trough_values,
                mode='markers',
                marker=dict(size=10, color='green', symbol='circle', line=dict(width=2, color='green')),
                name='Troughs'
            ))

    # Add a pattern-specific highlight area
    if pattern_type == 'pennant' and 'pole_start' in pattern_data and 'pennant_start' in pattern_data:
        # Shade the pole area
        pole_start = pattern_data['pole_start']
        pennant_start = pattern_data['pennant_start']
        pole_data = stock_data.iloc[pole_start:pennant_start]

        # Add a vertical line separating the pole and pennant
        if 'Price_Low' in extended_data.columns and 'Price_High' in extended_data.columns:
            fig.add_shape(
                type="line",
                x0=pole_data['Date'].iloc[-1],
                y0=extended_data['Price_Low'].min(),  # Corrected from 'Low' to 'Price_Low'
                x1=pole_data['Date'].iloc[-1],
                y1=extended_data['Price_High'].max(),  # Ensure 'Price_High' is used here as well
                line=dict(
                    color='blue',
                    width=1,
                    dash='dot',
                )
            )
        else:
            raise ValueError("Required columns 'Price_Low' or 'Price_High' not found in the DataFrame.")

        # Add annotations
        fig.add_annotation(
            x=pole_data['Date'].iloc[len(pole_data) // 2],
            y=pole_data['Price_High'].max(),
            text="Pole",
            showarrow=True,
            arrowhead=1,
            font=dict(color="blue")
        )

        fig.add_annotation(
            x=window_data['Date'].iloc[len(window_data) // 2],
            y=window_data['Price_High'].max(),
            text="Pennant",
            showarrow=True,
            arrowhead=1,
            font=dict(color="blue")
        )

    # Set the chart title and axis labels
    pattern_name_map = {
        'cup_with_handle': 'Cup with Handle',
        'head_and_shoulders': 'Head and Shoulders',
        'pennant': 'Pennant',
        'double_top': 'Double Top',
        'double_bottom': 'Double Bottom',
        'triple_top': 'Triple Top',
        'triple_bottom': 'Triple Bottom',
        'ascending_corridor': 'Ascending Corridor',
        'descending_corridor': 'Descending Corridor',
        'neutral_rectangle': 'Neutral Rectangle',
        'diverging_rectangle': 'Diverging Rectangle',
        'ascending_triangle': 'Ascending Triangle'
    }

    pattern_name = pattern_name_map.get(pattern_type, pattern_type.replace('_', ' ').title())
    fig.update_layout(
        title=f"{pattern_name} Pattern for {pattern_data['ticker']} ({pattern_data['start_date']} to {pattern_data['end_date']})",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
            scaleanchor="y",
            scaleratio=0.2,
            constraintoward="bottom",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=800,
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig