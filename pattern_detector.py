import pandas as pd
import numpy as np
from datetime import datetime
import scipy.signal as signal

def detect_all_patterns(stock_data, ticker):
    """
    Runs all pattern detection algorithms on the given stock data
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
    
    Returns:
        dict: Dictionary with detected patterns
    """
    patterns = {}
    
        # Ensure 'Price_Close' column is present
    if 'Price_Close' not in stock_data.columns:
       raise ValueError(f"Stock data for {ticker} must contain a 'Price_Close' column.")
    
    # Run each pattern detection function
    cup_with_handle = detect_cup_with_handle(stock_data, ticker)
    if cup_with_handle:
        patterns['cup_with_handle'] = cup_with_handle
        
    head_and_shoulders = detect_head_and_shoulders(stock_data, ticker)
    if head_and_shoulders:
        patterns['head_and_shoulders'] = head_and_shoulders
    
    pennant = detect_pennant(stock_data, ticker)
    if pennant:
        patterns['pennant'] = pennant
    
    double_top = detect_double_top(stock_data, ticker)
    if double_top:
        patterns['double_top'] = double_top
    
    double_bottom = detect_double_bottom(stock_data, ticker)
    if double_bottom:
        patterns['double_bottom'] = double_bottom
    
    triple_top = detect_triple_top(stock_data, ticker)
    if triple_top:
        patterns['triple_top'] = triple_top
    
    triple_bottom = detect_triple_bottom(stock_data, ticker)
    if triple_bottom:
        patterns['triple_bottom'] = triple_bottom
    
    ascending_corridor = detect_ascending_corridor(stock_data, ticker)
    if ascending_corridor:
        patterns['ascending_corridor'] = ascending_corridor
    
    descending_corridor = detect_descending_corridor(stock_data, ticker)
    if descending_corridor:
        patterns['descending_corridor'] = descending_corridor
    
    neutral_rectangle = detect_neutral_rectangle(stock_data, ticker)
    if neutral_rectangle:
        patterns['neutral_rectangle'] = neutral_rectangle
    
    diverging_rectangle = detect_diverging_rectangle(stock_data, ticker)
    if diverging_rectangle:
        patterns['diverging_rectangle'] = diverging_rectangle
    
    ascending_triangle = detect_ascending_triangle(stock_data, ticker)
    if ascending_triangle:
        patterns['ascending_triangle'] = ascending_triangle
    
    return patterns

def detect_peaks_and_troughs(data, order=10, prominence=0.02):
    """
    Detects peaks and troughs in the data series
    
    Args:
        data (pd.Series): Price data
        order (int): How many points on each side to use for peak/trough comparison
        prominence (float): Minimum prominence of peaks/troughs
        
    Returns:
        tuple: (peaks, troughs) indices
    """
    # Ensure data is a pandas Series
    if isinstance(data, pd.DataFrame):
        if 'Price_Close' in data.columns:
            data = data['Price_Close']
        else:
            raise ValueError("DataFrame must contain a 'Price_Close' column.")
    elif not isinstance(data, pd.Series):
        raise TypeError("Input must be a pandas Series or DataFrame.")

    # Detect peaks
    peaks, _ = signal.find_peaks(data.values, distance=order, prominence=prominence * np.max(data))

    # Detect troughs (by inverting the data and finding peaks)
    troughs, _ = signal.find_peaks(-data.values, distance=order, prominence=prominence * np.max(data))

    return peaks, troughs

    
def calculate_support_resistance(data, peaks, troughs):
    """
    Calculates support and resistance levels
    
    Args:
        data (pd.Series or pd.DataFrame): Price data
        peaks (np.array): Indices of peaks
        troughs (np.array): Indices of troughs
        
    Returns:
        tuple: (support, resistance) values
    """
    # Ensure data is a pandas Series
    if isinstance(data, pd.DataFrame):
        if 'Price_Close' in data.columns:
            data = data['Price_Close']
        else:
            raise ValueError("DataFrame must contain a 'Price_Close' column.")
    elif not isinstance(data, pd.Series):
        raise TypeError("Input must be a pandas Series or DataFrame.")

    resistance = None
    support = None

    if len(peaks) > 0:
        resistance = np.mean(data.iloc[peaks])

    if len(troughs) > 0:
        support = np.mean(data.iloc[troughs])

    return support, resistance

def detect_cup_with_handle(stock_data, ticker, window=120):
    """
    Detects Cup with Handle pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
    
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 2 peaks and 1 trough
        if len(peaks) < 2 or len(troughs) < 1:
            continue
        
        # Check for cup shape: two similar peaks with a trough in the middle
        if len(peaks) >= 2 and len(troughs) >= 1:
            # Peaks should be at similar heights (within 5%)
            peak1_val = window_data['Price_Close'].iloc[peaks[0]]
            peak2_val = window_data['Price_Close'].iloc[peaks[-1]]
            
            if abs(peak1_val - peak2_val) / peak1_val < 0.05:
                # Trough should be in between and at least 10% below peaks
                trough_val = window_data['Price_Close'].iloc[troughs[int(len(troughs)/2)]]
                
                if trough_val < 0.9 * min(peak1_val, peak2_val):
                    # Check for handle - a small downward drift after second peak
                    if peaks[-1] < len(window_data) - 10:
                        handle_data = window_data.iloc[peaks[-1]:]
                        
                        if handle_data['Price_Close'].iloc[0] > handle_data['Price_Close'].iloc[5] and \
                           handle_data['Price_Close'].iloc[5] < handle_data['Price_Close'].iloc[-1]:
                            
                            # Calculate support and resistance
                            support, resistance = calculate_support_resistance(window_data['Price_Close'], peaks, troughs)
                            
                            # Found a cup with handle pattern
                            pattern = {
                                'ticker': ticker,
                                'pattern': 'cup_with_handle',
                                'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                                'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                                'support': support,
                                'resistance': resistance,
                                'peaks': peaks,
                                'troughs': troughs,
                                'window_start': i,
                                'window_end': i+window
                            }
                            
                            patterns.append(pattern)
    
    return patterns

def detect_head_and_shoulders(stock_data, ticker, window=120):
    """
    Detects Head and Shoulders pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 3 peaks and 2 troughs for head and shoulders
        if len(peaks) < 3 or len(troughs) < 2:
            continue
        
        # Check each sequence of 3 peaks
        for p in range(len(peaks) - 2):
            # Get 3 consecutive peaks
            left_shoulder = window_data['Price_Close'].iloc[peaks[p]]
            head = window_data['Price_Close'].iloc[peaks[p+1]]
            right_shoulder = window_data['Price_Close'].iloc[peaks[p+2]]
            
            # Check if middle peak (head) is higher than shoulders
            if head > left_shoulder * 1.05 and head > right_shoulder * 1.05:
                # Shoulders should be at similar heights (within 10%)
                if abs(left_shoulder - right_shoulder) / left_shoulder < 0.1:
                    # Calculate support (neckline) and resistance
                    support, resistance = calculate_support_resistance(window_data['Price_Close'], peaks, troughs)
                    
                    # Found a head and shoulders pattern
                    pattern = {
                        'ticker': ticker,
                        'pattern': 'head_and_shoulders',
                        'start_date': window_data.iloc[max(0, peaks[p]-5)]['Date'].strftime('%Y-%m-%d'),
                        'end_date': window_data.iloc[min(len(window_data)-1, peaks[p+2]+5)]['Date'].strftime('%Y-%m-%d'),
                        'support': support,  # The neckline
                        'resistance': resistance,
                        'peaks': [peaks[p], peaks[p+1], peaks[p+2]],
                        'troughs': troughs,
                        'window_start': i,
                        'window_end': i+window
                    }
                    
                    patterns.append(pattern)
    
    return patterns

def detect_pennant(stock_data, ticker, window=60):
    """
    Detects Pennant pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        # First check for strong move up or down (the pole)
        pole_data = stock_data.iloc[max(0, i-20):i]
        
        if len(pole_data) < 15:
            continue
            
        # Calculate the price change over the pole period
        price_change = (pole_data['Price_Close'].iloc[-1] - pole_data['Price_Close'].iloc[0]) / pole_data['Price_Close'].iloc[0]
        
        # The pole should show a strong move (at least 10%)
        if abs(price_change) < 0.1:
            continue
        
        # Now check for the pennant (converging highs and lows)
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if highs are trending down and lows are trending up
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For a pennant, highs trend down and lows trend up (converging)
        if high_slope < -0.01 and low_slope > 0.01:
            # Calculate support and resistance from the converging lines
            days = np.arange(len(window_data))
            high_fit = np.polyfit(days, window_data['Price_High'], 1)
            low_fit = np.polyfit(days, window_data['Price_Low'], 1)
            
            high_line = np.polyval(high_fit, days)
            low_line = np.polyval(low_fit, days)
            
            # Support/resistance are the ending values of these lines
            resistance = high_line[-1]
            support = low_line[-1]
            
            # Found a pennant pattern
            pattern = {
                'ticker': ticker,
                'pattern': 'pennant',
                'start_date': pole_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                'support': support,
                'resistance': resistance,
                'pole_start': max(0, i-20),
                'pennant_start': i,
                'pennant_end': i+window,
                'window_start': max(0, i-20),
                'window_end': i+window
            }
            
            patterns.append(pattern)
    
    return patterns

def detect_double_top(stock_data, ticker, window=60):
    """
    Detects Double Top pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 2 peaks and 1 trough
        if len(peaks) < 2 or len(troughs) < 1:
            continue
        
        # Check for double top: two similar peaks with a trough in between
        for p in range(len(peaks) - 1):
            peak1_val = window_data['Price_Close'].iloc[peaks[p]]
            peak2_val = window_data['Price_Close'].iloc[peaks[p+1]]
            
            # Peaks should be similar in height (within 3%)
            if abs(peak1_val - peak2_val) / peak1_val < 0.03:
                # Find troughs between the peaks
                between_troughs = [t for t in troughs if t > peaks[p] and t < peaks[p+1]]
                
                if between_troughs:
                    # Calculate support and resistance
                    support, resistance = calculate_support_resistance(window_data['Price_Close'], [peaks[p], peaks[p+1]], between_troughs)
                    
                    # Found a double top pattern
                    pattern = {
                        'ticker': ticker,
                        'pattern': 'double_top',
                        'start_date': window_data.iloc[max(0, peaks[p]-5)]['Date'].strftime('%Y-%m-%d'),
                        'end_date': window_data.iloc[min(len(window_data)-1, peaks[p+1]+5)]['Date'].strftime('%Y-%m-%d'),
                        'support': support,
                        'resistance': resistance,
                        'peaks': [peaks[p], peaks[p+1]],
                        'troughs': between_troughs,
                        'window_start': i,
                        'window_end': i+window
                    }
                    
                    patterns.append(pattern)
    
    return patterns

def detect_double_bottom(stock_data, ticker, window=60):
    """
    Detects Double Bottom pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 1 peak and 2 troughs
        if len(peaks) < 1 or len(troughs) < 2:
            continue
        
        # Check for double bottom: two similar troughs with a peak in between
        for t in range(len(troughs) - 1):
            trough1_val = window_data['Price_Close'].iloc[troughs[t]]
            trough2_val = window_data['Price_Close'].iloc[troughs[t+1]]
            
            # Troughs should be similar in height (within 3%)
            if abs(trough1_val - trough2_val) / trough1_val < 0.03:
                # Find peaks between the troughs
                between_peaks = [p for p in peaks if p > troughs[t] and p < troughs[t+1]]
                
                if between_peaks:
                    # Calculate support and resistance
                    support, resistance = calculate_support_resistance(window_data['Price_Close'], between_peaks, [troughs[t], troughs[t+1]])
                    
                    # Found a double bottom pattern
                    pattern = {
                        'ticker': ticker,
                        'pattern': 'double_bottom',
                        'start_date': window_data.iloc[max(0, troughs[t]-5)]['Date'].strftime('%Y-%m-%d'),
                        'end_date': window_data.iloc[min(len(window_data)-1, troughs[t+1]+5)]['Date'].strftime('%Y-%m-%d'),
                        'support': support,
                        'resistance': resistance,
                        'peaks': between_peaks,
                        'troughs': [troughs[t], troughs[t+1]],
                        'window_start': i,
                        'window_end': i+window
                    }
                    
                    patterns.append(pattern)
    
    return patterns

def detect_triple_top(stock_data, ticker, window=90):
    """
    Detects Triple Top pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 3 peaks and 2 troughs
        if len(peaks) < 3 or len(troughs) < 2:
            continue
        
        # Check for triple top: three similar peaks
        for p in range(len(peaks) - 2):
            peak1_val = window_data['Price_Close'].iloc[peaks[p]]
            peak2_val = window_data['Price_Close'].iloc[peaks[p+1]]
            peak3_val = window_data['Price_Close'].iloc[peaks[p+2]]
            
            # Peaks should be similar in height (within 5%)
            peak_avg = (peak1_val + peak2_val + peak3_val) / 3
            if (abs(peak1_val - peak_avg) / peak_avg < 0.05 and
                abs(peak2_val - peak_avg) / peak_avg < 0.05 and
                abs(peak3_val - peak_avg) / peak_avg < 0.05):
                
                # Calculate support (neckline) and resistance
                between_troughs = [t for t in troughs if t > peaks[p] and t < peaks[p+2]]
                
                if between_troughs:
                    support, resistance = calculate_support_resistance(window_data['Price_Close'], [peaks[p], peaks[p+1], peaks[p+2]], between_troughs)
                    
                    # Found a triple top pattern
                    pattern = {
                        'ticker': ticker,
                        'pattern': 'triple_top',
                        'start_date': window_data.iloc[max(0, peaks[p]-5)]['Date'].strftime('%Y-%m-%d'),
                        'end_date': window_data.iloc[min(len(window_data)-1, peaks[p+2]+5)]['Date'].strftime('%Y-%m-%d'),
                        'support': support,
                        'resistance': resistance,
                        'peaks': [peaks[p], peaks[p+1], peaks[p+2]],
                        'troughs': between_troughs,
                        'window_start': i,
                        'window_end': i+window
                    }
                    
                    patterns.append(pattern)
    
    return patterns

def detect_triple_bottom(stock_data, ticker, window=90):
    """
    Detects Triple Bottom pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get peaks and troughs
        peaks, troughs = detect_peaks_and_troughs(window_data['Price_Close'], order=5)
        
        # Need at least 2 peaks and 3 troughs
        if len(peaks) < 2 or len(troughs) < 3:
            continue
        
        # Check for triple bottom: three similar troughs
        for t in range(len(troughs) - 2):
            trough1_val = window_data['Price_Close'].iloc[troughs[t]]
            trough2_val = window_data['Price_Close'].iloc[troughs[t+1]]
            trough3_val = window_data['Price_Close'].iloc[troughs[t+2]]
            
            # Troughs should be similar in height (within 5%)
            trough_avg = (trough1_val + trough2_val + trough3_val) / 3
            if (abs(trough1_val - trough_avg) / trough_avg < 0.05 and
                abs(trough2_val - trough_avg) / trough_avg < 0.05 and
                abs(trough3_val - trough_avg) / trough_avg < 0.05):
                
                # Calculate support and resistance (neckline)
                between_peaks = [p for p in peaks if p > troughs[t] and p < troughs[t+2]]
                
                if between_peaks:
                    support, resistance = calculate_support_resistance(window_data['Price_Close'], between_peaks, [troughs[t], troughs[t+1], troughs[t+2]])
                    
                    # Found a triple bottom pattern
                    pattern = {
                        'ticker': ticker,
                        'pattern': 'triple_bottom',
                        'start_date': window_data.iloc[max(0, troughs[t]-5)]['Date'].strftime('%Y-%m-%d'),
                        'end_date': window_data.iloc[min(len(window_data)-1, troughs[t+2]+5)]['Date'].strftime('%Y-%m-%d'),
                        'support': support,
                        'resistance': resistance,
                        'peaks': between_peaks,
                        'troughs': [troughs[t], troughs[t+1], troughs[t+2]],
                        'window_start': i,
                        'window_end': i+window
                    }
                    
                    patterns.append(pattern)
    
    return patterns

def detect_ascending_corridor(stock_data, ticker, window=60):
    """
    Detects Ascending Corridor pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if both highs and lows are trending up
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For an ascending corridor, both slopes should be positive and similar
        if high_slope > 0.01 and low_slope > 0.01 and abs(high_slope - low_slope) / high_slope < 0.3:
            # Calculate support and resistance from the trend lines
            days = np.arange(len(window_data))
            high_fit = np.polyfit(days, window_data['Price_High'], 1)
            low_fit = np.polyfit(days, window_data['Price_Low'], 1)
            
            high_line = np.polyval(high_fit, days)
            low_line = np.polyval(low_fit, days)
            
            # Support/resistance are the ending values of these lines
            resistance = high_line[-1]
            support = low_line[-1]
            
            # Found an ascending corridor pattern
            pattern = {
                'ticker': ticker,
                'pattern': 'ascending_corridor',
                'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                'support': support,
                'resistance': resistance,
                'high_slope': high_slope,
                'low_slope': low_slope,
                'high_line': high_line.tolist(),
                'low_line': low_line.tolist(),
                'window_start': i,
                'window_end': i+window
            }
            
            patterns.append(pattern)
    
    return patterns

def detect_descending_corridor(stock_data, ticker, window=60):
    """
    Detects Descending Corridor pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if both highs and lows are trending down
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For a descending corridor, both slopes should be negative and similar
        if high_slope < -0.01 and low_slope < -0.01 and abs(high_slope - low_slope) / abs(high_slope) < 0.3:
            # Calculate support and resistance from the trend lines
            days = np.arange(len(window_data))
            high_fit = np.polyfit(days, window_data['Price_High'], 1)
            low_fit = np.polyfit(days, window_data['Price_Low'], 1)
            
            high_line = np.polyval(high_fit, days)
            low_line = np.polyval(low_fit, days)
            
            # Support/resistance are the ending values of these lines
            resistance = high_line[-1]
            support = low_line[-1]
            
            # Found a descending corridor pattern
            pattern = {
                'ticker': ticker,
                'pattern': 'descending_corridor',
                'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                'support': support,
                'resistance': resistance,
                'high_slope': high_slope,
                'low_slope': low_slope,
                'high_line': high_line.tolist(),
                'low_line': low_line.tolist(),
                'window_start': i,
                'window_end': i+window
            }
            
            patterns.append(pattern)
    
    return patterns

def detect_neutral_rectangle(stock_data, ticker, window=60):
    """
    Detects Neutral Rectangle pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if both highs and lows are flat (minimal slope)
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For a neutral rectangle, both slopes should be close to 0
        if abs(high_slope) < 0.01 and abs(low_slope) < 0.01:
            # Calculate the average high and low values
            resistance = np.mean(high_prices)
            support = np.mean(low_prices)
            
            # Make sure there's a significant gap between support and resistance
            if (resistance - support) / support > 0.03:
                # Found a neutral rectangle pattern
                pattern = {
                    'ticker': ticker,
                    'pattern': 'neutral_rectangle',
                    'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                    'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                    'support': support,
                    'resistance': resistance,
                    'high_slope': high_slope,
                    'low_slope': low_slope,
                    'window_start': i,
                    'window_end': i+window
                }
                
                patterns.append(pattern)
    
    return patterns

def detect_diverging_rectangle(stock_data, ticker, window=60):
    """
    Detects Diverging Rectangle pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if highs are trending up and lows are trending down
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For a diverging rectangle, high slope is positive and low slope is negative
        if high_slope > 0.01 and low_slope < -0.01:
            # Calculate support and resistance from the trend lines
            days = np.arange(len(window_data))
            high_fit = np.polyfit(days, window_data['Price_High'], 1)
            low_fit = np.polyfit(days, window_data['Price_Low'], 1)
            
            high_line = np.polyval(high_fit, days)
            low_line = np.polyval(low_fit, days)
            
            # Support/resistance are the ending values of these lines
            resistance = high_line[-1]
            support = low_line[-1]
            
            # Found a diverging rectangle pattern
            pattern = {
                'ticker': ticker,
                'pattern': 'diverging_rectangle',
                'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                'support': support,
                'resistance': resistance,
                'high_slope': high_slope,
                'low_slope': low_slope,
                'high_line': high_line.tolist(),
                'low_line': low_line.tolist(),
                'window_start': i,
                'window_end': i+window
            }
            
            patterns.append(pattern)
    
    return patterns

def detect_ascending_triangle(stock_data, ticker, window=60):
    """
    Detects Ascending Triangle pattern
    
    Args:
        stock_data (pd.DataFrame): Stock price data
        ticker (str): Ticker symbol
        window (int): Window size to look for pattern
        
    Returns:
        list: Detected patterns with metadata
    """
    patterns = []
    
    if len(stock_data) < window:
        return patterns
        
    # Look for windows of data
    for i in range(len(stock_data) - window):
        window_data = stock_data.iloc[i:i+window]
        
        # Get the high and low trends
        high_prices = window_data['Price_High'].values
        low_prices = window_data['Price_Low'].values
        
        # Check if highs are flat and lows are trending up
        # by fitting linear regression
        x = np.arange(len(high_prices))
        high_slope = np.polyfit(x, high_prices, 1)[0]
        low_slope = np.polyfit(x, low_prices, 1)[0]
        
        # For an ascending triangle, high slope is close to 0 and low slope is positive
        if abs(high_slope) < 0.01 and low_slope > 0.01:
            # Calculate support and resistance from the trend lines
            days = np.arange(len(window_data))
            high_fit = np.polyfit(days, window_data['Price_High'], 1)
            low_fit = np.polyfit(days, window_data['Price_Low'], 1)
            
            high_line = np.polyval(high_fit, days)
            low_line = np.polyval(low_fit, days)
            
            # Support/resistance are the ending values of these lines
            resistance = high_line[-1]
            support = low_line[-1]
            
            # Make sure there's convergence
            if (resistance - support) / support < 0.1:
                # Found an ascending triangle pattern
                pattern = {
                    'ticker': ticker,
                    'pattern': 'ascending_triangle',
                    'start_date': window_data.iloc[0]['Date'].strftime('%Y-%m-%d'),
                    'end_date': window_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),
                    'support': support,
                    'resistance': resistance,
                    'high_slope': high_slope,
                    'low_slope': low_slope,
                    'high_line': high_line.tolist(),
                    'low_line': low_line.tolist(),
                    'window_start': i,
                    'window_end': i+window
                }
                
                patterns.append(pattern)
    
    return patterns
