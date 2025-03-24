import streamlit as st
import pandas as pd
import time

from data_loader import fetch_stock_data, get_sp500_symbols
from pattern_detector import detect_all_patterns
from visualization import plot_pattern_chart

# Function to flatten and rename MultiIndex columns
def flatten_columns(stock_data, ticker):
    """
    Flattens MultiIndex columns and renames them to simple column names.

    Args:
        stock_data (pd.DataFrame): Stock data with MultiIndex columns
        ticker (str): Ticker symbol

    Returns:
        pd.DataFrame: Stock data with simple column names
    """
    if isinstance(stock_data.columns, pd.MultiIndex):
        # Flatten the MultiIndex columns
        stock_data.columns = stock_data.columns.map('_'.join).str.strip('_')
        
        # Strip the ticker suffix from column names (e.g., "Close_MMM" -> "Close")
        stock_data.columns = stock_data.columns.str.replace(f"_{ticker}", "", regex=False)
    
    return stock_data

# Page configuration
st.set_page_config(
    page_title="Stockinator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title
st.title("🚀 The Stockinator")
st.markdown("### Technical Chart Pattern Analysis Tool")
st.markdown("---")

# Initialize session state variables
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "patterns_detected" not in st.session_state:
    st.session_state.patterns_detected = False
if "all_patterns" not in st.session_state:
    st.session_state.all_patterns = {}
if "tickers" not in st.session_state:
    st.session_state.tickers = []
if "stock_data" not in st.session_state:
    st.session_state.stock_data = {}
    
# Sidebar - App Controls
with st.sidebar:
    st.header("Controls")
    
    # Load data button
    if not st.session_state.data_loaded:
        if st.button("Load S&P 500 Stock Data", use_container_width=True):
            with st.spinner("Loading S&P 500 stock data..."):
                try:
                    # Get S&P 500 symbols (limited to avoid rate limiting)
                    st.session_state.tickers = get_sp500_symbols()[:50]  # Limit to 50 for demo purposes
                    
                    # Progress bar for loading data
                    progress_bar = st.progress(0)
                    for i, ticker in enumerate(st.session_state.tickers):
                        try:
                            # Fetch stock data
                            stock_data = fetch_stock_data(ticker)
                            
                            # Flatten and rename MultiIndex columns
                            stock_data = flatten_columns(stock_data, ticker)
                            
                            # Store the processed data in session state
                            st.session_state.stock_data[ticker] = stock_data
                            
                            # Update progress bar
                            progress_percentage = (i + 1) / len(st.session_state.tickers)
                            progress_bar.progress(progress_percentage, f"Loading {ticker}...")
                        except Exception as e:
                            st.error(f"Error loading {ticker}: {str(e)}")
                            continue  # Skip this ticker and continue with the next one
                            
                    st.session_state.data_loaded = True
                    progress_bar.empty()
                    st.success(f"Successfully loaded {len(st.session_state.stock_data)} stocks")
                except Exception as e:
                    st.error(f"Failed to load stock data: {str(e)}")
    else:
        st.success(f"Data loaded for {len(st.session_state.stock_data)} stocks")
        
        # Detect patterns button
        if not st.session_state.patterns_detected:
            if st.button("Detect Technical Patterns", use_container_width=True):
                with st.spinner("Analyzing patterns..."):
                    try:
                        progress_bar = st.progress(0)
                        for i, ticker in enumerate(st.session_state.stock_data.keys()):
                            try:
                                if ticker in st.session_state.stock_data:
                                    patterns = detect_all_patterns(st.session_state.stock_data[ticker], ticker)
                                    
                                    # Update all patterns dictionary
                                    for pattern_name, pattern_instances in patterns.items():
                                        if pattern_name not in st.session_state.all_patterns:
                                            st.session_state.all_patterns[pattern_name] = []
                                        
                                        for instance in pattern_instances:
                                            st.session_state.all_patterns[pattern_name].append(instance)
                                
                                progress_percentage = (i + 1) / len(st.session_state.stock_data)
                                progress_bar.progress(progress_percentage, f"Analyzing {ticker}...")
                            except Exception as e:
                                st.warning(f"Error analyzing {ticker}: {str(e)}")
                                continue
                        
                        st.session_state.patterns_detected = True
                        progress_bar.empty()
                        st.success("Pattern detection completed")
                    except Exception as e:
                        st.error(f"Failed to detect patterns: {str(e)}")
        else:
            st.success("Patterns detected")
            
            # Reset button
            if st.button("Start Over", use_container_width=True):
                st.session_state.data_loaded = False
                st.session_state.patterns_detected = False
                st.session_state.all_patterns = {}
                st.session_state.tickers = []
                st.session_state.stock_data = {}
                st.rerun()
    
    # About section
    st.markdown("---")
    st.markdown("""
    **About The Stockinator**  
    This app analyzes stock data from Yahoo Finance and identifies common technical chart patterns.
    
    **Technical Patterns:**
    - Cup with Handle
    - Head and Shoulders
    - Pennant
    - Double Top/Bottom
    - Triple Top/Bottom
    - Ascending/Descending Corridors
    - Rectangle Patterns
    - Ascending Triangle
    """)

# Main content area
if st.session_state.patterns_detected:
    # Create a section for all detected patterns
    st.header("Detected Technical Patterns")
    
    # Tabs for pattern categories
    tab_names = [
        "Cup with Handle", 
        "Head and Shoulders", 
        "Pennant", 
        "Double Patterns",
        "Triple Patterns", 
        "Corridors", 
        "Rectangles", 
        "Triangles"
    ]
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Cup with Handle
        st.subheader("Cup with Handle Patterns")
        if "cup_with_handle" in st.session_state.all_patterns and st.session_state.all_patterns["cup_with_handle"]:
            patterns = st.session_state.all_patterns["cup_with_handle"]
            pattern_options = [f"Cup with Handle - {p['ticker']}" for p in patterns]
            selected = st.selectbox("Select pattern to view", pattern_options, key="cup_select")
            
            if selected:
                pattern_idx = pattern_options.index(selected)
                pattern_data = patterns[pattern_idx]
                st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                fig = plot_pattern_chart(
                    st.session_state.stock_data[pattern_data['ticker']], 
                    pattern_data
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Cup with Handle patterns detected")
    
    with tabs[1]:  # Head and Shoulders
        st.subheader("Head and Shoulders Patterns")
        if "head_and_shoulders" in st.session_state.all_patterns and st.session_state.all_patterns["head_and_shoulders"]:
            patterns = st.session_state.all_patterns["head_and_shoulders"]
            pattern_options = [f"Head and Shoulders - {p['ticker']}" for p in patterns]
            selected = st.selectbox("Select pattern to view", pattern_options, key="hs_select")
            
            if selected:
                pattern_idx = pattern_options.index(selected)
                pattern_data = patterns[pattern_idx]
                st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                fig = plot_pattern_chart(
                    st.session_state.stock_data[pattern_data['ticker']], 
                    pattern_data
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Head and Shoulders patterns detected")
            
    with tabs[2]:  # Pennant
        st.subheader("Pennant Patterns")
        if "pennant" in st.session_state.all_patterns and st.session_state.all_patterns["pennant"]:
            patterns = st.session_state.all_patterns["pennant"]
            pattern_options = [f"Pennant - {p['ticker']}" for p in patterns]
            selected = st.selectbox("Select pattern to view", pattern_options, key="pennant_select")
            
            if selected:
                pattern_idx = pattern_options.index(selected)
                pattern_data = patterns[pattern_idx]
                st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                fig = plot_pattern_chart(
                    st.session_state.stock_data[pattern_data['ticker']], 
                    pattern_data
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Pennant patterns detected")
    
    with tabs[3]:  # Double Patterns
        st.subheader("Double Top/Bottom Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Double Top")
            if "double_top" in st.session_state.all_patterns and st.session_state.all_patterns["double_top"]:
                patterns = st.session_state.all_patterns["double_top"]
                pattern_options = [f"Double Top - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="dt_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Double Top patterns detected")
        
        with col2:
            st.markdown("### Double Bottom")
            if "double_bottom" in st.session_state.all_patterns and st.session_state.all_patterns["double_bottom"]:
                patterns = st.session_state.all_patterns["double_bottom"]
                pattern_options = [f"Double Bottom - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="db_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Double Bottom patterns detected")
    
    with tabs[4]:  # Triple Patterns
        st.subheader("Triple Top/Bottom Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Triple Top")
            if "triple_top" in st.session_state.all_patterns and st.session_state.all_patterns["triple_top"]:
                patterns = st.session_state.all_patterns["triple_top"]
                pattern_options = [f"Triple Top - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="tt_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Triple Top patterns detected")
        
        with col2:
            st.markdown("### Triple Bottom")
            if "triple_bottom" in st.session_state.all_patterns and st.session_state.all_patterns["triple_bottom"]:
                patterns = st.session_state.all_patterns["triple_bottom"]
                pattern_options = [f"Triple Bottom - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="tb_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Triple Bottom patterns detected")
    
    with tabs[5]:  # Corridors
        st.subheader("Ascending/Descending Corridor Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Ascending Corridor")
            if "ascending_corridor" in st.session_state.all_patterns and st.session_state.all_patterns["ascending_corridor"]:
                patterns = st.session_state.all_patterns["ascending_corridor"]
                pattern_options = [f"Ascending Corridor - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="ac_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Ascending Corridor patterns detected")
        
        with col2:
            st.markdown("### Descending Corridor")
            if "descending_corridor" in st.session_state.all_patterns and st.session_state.all_patterns["descending_corridor"]:
                patterns = st.session_state.all_patterns["descending_corridor"]
                pattern_options = [f"Descending Corridor - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="dc_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Descending Corridor patterns detected")
    
    with tabs[6]:  # Rectangles
        st.subheader("Rectangle Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Neutral Rectangle")
            if "neutral_rectangle" in st.session_state.all_patterns and st.session_state.all_patterns["neutral_rectangle"]:
                patterns = st.session_state.all_patterns["neutral_rectangle"]
                pattern_options = [f"Neutral Rectangle - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="nr_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Neutral Rectangle patterns detected")
        
        with col2:
            st.markdown("### Diverging Rectangle")
            if "diverging_rectangle" in st.session_state.all_patterns and st.session_state.all_patterns["diverging_rectangle"]:
                patterns = st.session_state.all_patterns["diverging_rectangle"]
                pattern_options = [f"Diverging Rectangle - {p['ticker']}" for p in patterns]
                selected = st.selectbox("Select pattern to view", pattern_options, key="dr_select")
                
                if selected:
                    pattern_idx = pattern_options.index(selected)
                    pattern_data = patterns[pattern_idx]
                    st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                    fig = plot_pattern_chart(
                        st.session_state.stock_data[pattern_data['ticker']], 
                        pattern_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Diverging Rectangle patterns detected")
    
    with tabs[7]:  # Triangles
        st.subheader("Ascending Triangle Patterns")
        if "ascending_triangle" in st.session_state.all_patterns and st.session_state.all_patterns["ascending_triangle"]:
            patterns = st.session_state.all_patterns["ascending_triangle"]
            pattern_options = [f"Ascending Triangle - {p['ticker']}" for p in patterns]
            selected = st.selectbox("Select pattern to view", pattern_options, key="at_select")
            
            if selected:
                pattern_idx = pattern_options.index(selected)
                pattern_data = patterns[pattern_idx]
                st.markdown(f"**{pattern_data['ticker']}** - Pattern detected from {pattern_data['start_date']} to {pattern_data['end_date']}")
                fig = plot_pattern_chart(
                    st.session_state.stock_data[pattern_data['ticker']], 
                    pattern_data
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Ascending Triangle patterns detected")

elif st.session_state.data_loaded:
    # Show loading state while detecting patterns
    st.info("Data has been loaded. Use the sidebar to detect technical patterns.")
    
    # Show sample of loaded data
    st.header("Loaded Stock Data Preview")
    if st.session_state.tickers:
        ticker = st.selectbox("Select a ticker to preview data", st.session_state.tickers)
        if ticker in st.session_state.stock_data:
            st.dataframe(st.session_state.stock_data[ticker].tail(10))
        else:
            st.error(f"No data available for {ticker}")
else:
    # Initial state - show instructions
    st.info("Welcome to the Stockinator! 📈 To get started, click 'Load S&P 500 Stock Data' in the sidebar.")
    
    
    st.markdown("""
    <div style="display: flex; justify-content: center;">
                                                  ## How to use the Stockinator:

          1. **Load Stock Data**: Click the button in the sidebar to fetch the last year of data for S&P 500 stocks.
          2. **Detect Patterns**: After data is loaded, click the "Detect Technical Patterns" button.
          3. **View Patterns**: Browse through the tabs to view detected patterns by category.
          4. **Analyze Charts**: Select a specific pattern-ticker combination to view a detailed chart with support and resistance levels.
         
          
          ### Supported Technical Patterns:
              - **Cup with Handle**: A bullish continuation pattern.
              - **Head and Shoulders**: A reversal pattern signaling a trend change.
              - **Pennant**: A continuation pattern after a strong price movement.
              - **Double Top/Bottom**: Reversal patterns indicating potential trend reversals.
              - **Triple Top/Bottom**: Stronger versions of double top/bottom patterns.
              - **Ascending/Descending Corridors**: Continuation patterns with parallel trendlines.
              - **Rectangle Patterns**: Consolidation patterns indicating equilibrium.
              - **Ascending Triangle**: A bullish continuation pattern with a flat resistance line and rising support.
    </div>
    """, unsafe_allow_html=True)

# Donation button at the bottom
st.markdown("---")  # Add a horizontal line for separation
import streamlit as st

st.markdown(
    """
    <a href="https://www.paypal.com/donate/?business=HH5K872YT7UBQ&no_recurring=0&currency_code=USD" target="_blank">
        <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" alt="Donate with PayPal">
    </a>
    """,
    unsafe_allow_html=True
)