import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def format_pattern_name(pattern_type):
    """
    Formats a pattern type name into a readable format
    
    Args:
        pattern_type (str): The pattern type key
        
    Returns:
        str: Formatted pattern name
    """
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
    
    return pattern_name_map.get(pattern_type, pattern_type.replace('_', ' ').title())

def get_pattern_description(pattern_type):
    """
    Returns a description of a technical pattern
    
    Args:
        pattern_type (str): The pattern type key
        
    Returns:
        str: Pattern description
    """
    pattern_descriptions = {
        'cup_with_handle': """
        The Cup with Handle is a bullish continuation pattern that marks a consolidation period followed by a breakout.
        It consists of a rounded bottom (cup) followed by a slight downward drift (handle).
        The pattern is complete when the price breaks out above the resistance level formed by the cup.
        """,
        
        'head_and_shoulders': """
        The Head and Shoulders pattern is a reversal pattern that signals a trend change from bullish to bearish.
        It consists of three peaks: a central peak (head) that is higher than the two surrounding peaks (shoulders).
        The pattern is confirmed when the price breaks below the neckline drawn through the troughs between the peaks.
        """,
        
        'pennant': """
        The Pennant is a continuation pattern that forms after a strong price movement (the pole),
        followed by a consolidation period where the price converges in a small symmetrical triangle (the pennant).
        The pattern is complete when the price breaks out in the same direction as the initial movement.
        """,
        
        'double_top': """
        The Double Top is a bearish reversal pattern that forms after an uptrend.
        It consists of two consecutive peaks at approximately the same price level,
        with a moderate trough in between. The pattern is confirmed when the price breaks below the support level.
        """,
        
        'double_bottom': """
        The Double Bottom is a bullish reversal pattern that forms after a downtrend.
        It consists of two consecutive troughs at approximately the same price level,
        with a moderate peak in between. The pattern is confirmed when the price breaks above the resistance level.
        """,
        
        'triple_top': """
        The Triple Top is a bearish reversal pattern similar to the double top but with three peaks at approximately the same level.
        The pattern signals that the uptrend is ending and a downtrend may follow.
        It is confirmed when the price breaks below the support level.
        """,
        
        'triple_bottom': """
        The Triple Bottom is a bullish reversal pattern similar to the double bottom but with three troughs at approximately the same level.
        The pattern signals that the downtrend is ending and an uptrend may follow.
        It is confirmed when the price breaks above the resistance level.
        """,
        
        'ascending_corridor': """
        The Ascending Corridor (or Channel) is a bullish continuation pattern where price moves between two parallel upward-sloping trendlines.
        The lower trendline connects the lows and represents support, while the upper trendline connects the highs and represents resistance.
        Traders often buy near support and sell near resistance within the channel.
        """,
        
        'descending_corridor': """
        The Descending Corridor (or Channel) is a bearish continuation pattern where price moves between two parallel downward-sloping trendlines.
        The upper trendline connects the highs and represents resistance, while the lower trendline connects the lows and represents support.
        Traders often sell near resistance and buy near support within the channel.
        """,
        
        'neutral_rectangle': """
        The Neutral Rectangle (or Trading Range) occurs when price consolidates between two horizontal parallel trendlines.
        The upper line represents resistance, and the lower line represents support.
        This pattern indicates a period of equilibrium between buyers and sellers, with no clear direction.
        """,
        
        'diverging_rectangle': """
        The Diverging Rectangle (or Broadening Formation) occurs when price moves between two diverging trendlines.
        Unlike most patterns, this shows increasing volatility rather than consolidation.
        The upper line (resistance) slopes upward, while the lower line (support) slopes downward, indicating confusion in the market.
        """,
        
        'ascending_triangle': """
        The Ascending Triangle is a bullish continuation pattern characterized by a flat upper trendline (resistance) and an upward-sloping lower trendline (support).
        The pattern indicates that buyers are becoming more aggressive while sellers remain consistent at the resistance level.
        It typically results in an upward breakout through the resistance level.
        """
    }
    
    return pattern_descriptions.get(pattern_type, "No description available for this pattern.")

def calculate_success_rate(pattern_type):
    """
    Returns historical success rate information for a pattern type
    This is based on general research and studies on technical patterns,
    not specific to the implementation or data in this application.
    
    Args:
        pattern_type (str): The pattern type key
        
    Returns:
        dict: Success rate information
    """
    # These are estimated values based on technical analysis literature
    # Actual rates would vary based on specific implementations and market conditions
    pattern_success_rates = {
        'cup_with_handle': {'success_rate': '65%', 'confidence': 'High'},
        'head_and_shoulders': {'success_rate': '75%', 'confidence': 'High'},
        'pennant': {'success_rate': '70%', 'confidence': 'Medium'},
        'double_top': {'success_rate': '65%', 'confidence': 'Medium'},
        'double_bottom': {'success_rate': '65%', 'confidence': 'Medium'},
        'triple_top': {'success_rate': '78%', 'confidence': 'High'},
        'triple_bottom': {'success_rate': '78%', 'confidence': 'High'},
        'ascending_corridor': {'success_rate': '60%', 'confidence': 'Medium'},
        'descending_corridor': {'success_rate': '60%', 'confidence': 'Medium'},
        'neutral_rectangle': {'success_rate': '55%', 'confidence': 'Low'},
        'diverging_rectangle': {'success_rate': '50%', 'confidence': 'Low'},
        'ascending_triangle': {'success_rate': '72%', 'confidence': 'High'}
    }
    
    return pattern_success_rates.get(pattern_type, {'success_rate': 'Unknown', 'confidence': 'Unknown'})
