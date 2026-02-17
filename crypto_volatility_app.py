import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Crypto Volatility Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --charcoal: #1e2028;
        --slate-dark: #272a35;
        --slate-mid: #2f3342;
        --muted-blue: #4a6fa5;
        --faded-teal: #5b9a8b;
        --soft-beige: #c4b5a0;
        --warm-gray: #8a8697;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #2a2d3a 0%, #323648 100%);
        border: 1px solid #3a3e50;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        font-family: 'Monaco', 'Courier New', monospace;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #8a8697;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-sublabel {
        font-size: 0.85em;
        color: #8a8697;
        margin-top: 5px;
    }
    
    /* Welcome screen */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
    }
    
    .welcome-title {
        font-size: 3.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #4a6fa5, #5b9a8b, #c4b5a0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        animation: gradientShift 5s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .welcome-subtitle {
        font-size: 1.8em;
        color: #8a8697;
        margin-bottom: 20px;
    }
    
    .welcome-description {
        font-size: 1.1em;
        color: #8a8697;
        max-width: 700px;
        margin: 0 auto 40px;
        line-height: 1.6;
    }
    
    /* Model info box */
    .model-info {
        background: #2a2d3a;
        border: 1px solid #3a3e50;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    /* Stacked layout improvements */
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #272a35 0%, #1e2028 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'user_name' not in st.session_state:
    st.session_state.user_name = 'Guest Researcher'
if 'project_id' not in st.session_state:
    st.session_state.project_id = ''
if 'pattern' not in st.session_state:
    st.session_state.pattern = 'wave'
if 'amplitude' not in st.session_state:
    st.session_state.amplitude = 0.5
if 'frequency' not in st.session_state:
    st.session_state.frequency = 1.0
if 'drift' not in st.session_state:
    st.session_state.drift = 0.0
if 'noise' not in st.session_state:
    st.session_state.noise = 0.3
if 'data_points' not in st.session_state:
    st.session_state.data_points = 90
if 'price_data' not in st.session_state:
    st.session_state.price_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'data_seed' not in st.session_state:
    st.session_state.data_seed = np.random.randint(0, 1000000)

# Helper functions
def gaussian_random():
    """Generate Gaussian random number using Box-Muller transform"""
    u1 = np.random.random()
    u2 = np.random.random()
    return np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)

def generate_data():
    """Generate cryptocurrency price data based on current parameters"""
    # Create deterministic seed based on parameters + random seed
    # This ensures same parameters give consistent results, but different from other parameter sets
    param_hash = hash((
        st.session_state.pattern,
        st.session_state.amplitude,
        st.session_state.frequency,
        st.session_state.drift,
        st.session_state.noise,
        st.session_state.data_points,
        st.session_state.data_seed
    ))
    np.random.seed(abs(param_hash) % (2**31))
    
    base_price = 40000
    start_date = datetime(2024, 1, 1)
    data = []
    price = base_price
    
    for i in range(st.session_state.data_points):
        t = i / st.session_state.data_points
        date = start_date + timedelta(days=i)
        
        if st.session_state.pattern == 'wave':
            # Wave pattern: Pure sinusoidal behavior
            # Amplitude directly controls wave height
            # Frequency controls oscillation speed
            # Drift adds linear trend
            # Noise adds random perturbation
            wave = st.session_state.amplitude * 5000 * np.sin(2 * np.pi * st.session_state.frequency * t)
            trend = st.session_state.drift * 10000 * t
            noise_component = st.session_state.noise * np.random.randn() * 500
            
            price = base_price + wave + trend + noise_component
            
        else:
            # Random walk with drift
            # Amplitude controls step size
            # Drift adds directional bias
            # Noise adds additional randomness
            # Occasional large jumps based on amplitude
            
            daily_change = st.session_state.drift * 50  # Drift component
            random_step = st.session_state.amplitude * np.random.randn() * 500  # Random walk
            noise_component = st.session_state.noise * np.random.randn() * 300
            
            # Occasional jumps - more frequent with higher amplitude
            if np.random.random() < (0.03 + st.session_state.amplitude * 0.02):
                jump = np.random.randn() * 1500 * st.session_state.amplitude
            else:
                jump = 0
            
            price = price + daily_change + random_step + noise_component + jump
        
        price = max(price, 1000)  # Minimum price floor
        
        # Calculate realistic high/low based on intraday volatility
        # Higher amplitude = larger intraday ranges
        intraday_volatility = (st.session_state.amplitude * 600 + 
                              st.session_state.noise * 400 + 
                              200)
        
        high = price + abs(np.random.randn()) * intraday_volatility * 0.5
        low = price - abs(np.random.randn()) * intraday_volatility * 0.5
        low = max(low, 500)  # Floor for low price
        
        # Volume correlates with volatility and price changes
        base_volume = 5000
        volatility_volume = st.session_state.amplitude * 2000
        noise_volume = st.session_state.noise * 1500
        
        # Higher volume on larger price movements
        if i > 0:
            price_change_pct = abs((price - data[i-1]['price']) / data[i-1]['price'])
            movement_volume = price_change_pct * 20000
        else:
            movement_volume = 0
        
        volume = base_volume + volatility_volume + noise_volume + movement_volume
        volume = max(volume + np.random.randn() * 1000, 500)
        
        data.append({
            'date': date,
            'price': round(price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'volume': round(volume)
        })
    
    st.session_state.price_data = pd.DataFrame(data)
    st.session_state.last_update = time.time()

def calculate_metrics():
    """Calculate volatility and other metrics"""
    if st.session_state.price_data is None or len(st.session_state.price_data) < 2:
        return None
    
    df = st.session_state.price_data
    
    # Calculate returns
    returns = df['price'].pct_change().dropna()
    
    # Volatility metrics
    daily_vol = returns.std()
    annualized_vol = daily_vol * np.sqrt(252)
    
    # Average price
    avg_price = df['price'].mean()
    
    # Trend (linear regression slope)
    x = np.arange(len(df))
    y = df['price'].values
    slope = np.polyfit(x, y, 1)[0]
    
    # Stability score
    stability_score = max(0, min(100, 100 - annualized_vol * 100))
    
    return {
        'volatility': annualized_vol,
        'avg_price': avg_price,
        'slope': slope,
        'stability': stability_score,
        'daily_vol': daily_vol
    }

def render_welcome_page():
    """Render the welcome landing page"""
    st.markdown("""
    <div class="welcome-container">
        <div style="font-size: 80px; margin-bottom: 30px;">📈</div>
        <h1 class="welcome-title">Crypto Volatility Visualizer</h1>
        <h2 class="welcome-subtitle">Mathematics for AI Dashboard</h2>
        <p class="welcome-description">
            Explore cryptocurrency stability and volatility through interactive mathematical models. 
            Adjust wave patterns, amplitude, frequency, and drift to understand market behaviour 
            using AI-driven mathematics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Start Dashboard", type="primary", use_container_width=True):
            st.session_state.page = 'entry'
            st.rerun()
    
    st.markdown("""
    <p style="text-align: center; color: #8a8697; font-size: 0.8em; margin-top: 60px; opacity: 0.6;">
        Academic Research Project · Mathematical Modelling & Visualization
    </p>
    """, unsafe_allow_html=True)

def render_entry_page():
    """Render the user entry page"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 60px; margin-bottom: 20px;">👤</div>
            <h2 style="color: #c9c5be;">Welcome to Dashboard</h2>
            <p style="color: #8a8697;">Enter your details to begin exploring</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("entry_form"):
            user_name = st.text_input(
                "Your Name",
                placeholder="e.g. Dr. Sarah Chen",
                help="Enter your name to personalize the dashboard"
            )
            
            project_id = st.text_input(
                "Project ID (optional)",
                placeholder="e.g. MATH-AI-2024",
                help="Optional project identifier"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("Enter Dashboard", type="primary", use_container_width=True)
            with col_btn2:
                skip = st.form_submit_button("Skip → Guest", use_container_width=True)
            
            if submitted:
                st.session_state.user_name = user_name if user_name else "Guest Researcher"
                st.session_state.project_id = project_id
                st.session_state.page = 'dashboard'
                st.session_state.data_seed = np.random.randint(0, 1000000)
                generate_data()
                st.rerun()
            
            if skip:
                st.session_state.user_name = "Guest Researcher"
                st.session_state.project_id = ""
                st.session_state.page = 'dashboard'
                st.session_state.data_seed = np.random.randint(0, 1000000)
                generate_data()
                st.rerun()

def render_dashboard():
    """Render the main dashboard"""
    
    # Header
    col_h1, col_h2, col_h3 = st.columns([2, 3, 2])
    with col_h1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 32px;">📈</div>
            <div>
                <div style="font-weight: bold; font-size: 1.1em;">Crypto Volatility Visualizer</div>
                <div style="color: #8a8697; font-size: 0.85em;">Real-time Mathematical Modelling</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_h3:
        st.markdown(f"""
        <div style="text-align: right; padding: 10px;">
            <div style="color: #8a8697; font-family: monospace; font-size: 0.9em;">
                {st.session_state.user_name}
            </div>
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-top: 5px;">
                <div style="width: 8px; height: 8px; background: #5b9a8b; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <span style="color: #8a8697; font-size: 0.85em;">Live</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #3a3e50;'>", unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚡ Pattern Model")
        
        pattern = st.radio(
            "Select Pattern",
            options=['wave', 'random'],
            format_func=lambda x: "🌊 Wave Pattern" if x == 'wave' else "🎲 Random Market Jumps",
            help="Wave: Sine/cosine behavior | Random: Noise simulation model"
        )
        
        if pattern != st.session_state.pattern:
            st.session_state.pattern = pattern
            # Generate new seed for different data
            st.session_state.data_seed = np.random.randint(0, 1000000)
            generate_data()
            st.rerun()
        
        st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #3a3e50;'>", unsafe_allow_html=True)
        
        st.markdown("### 🎚️ Parameters")
        
        st.info("**💡 How parameters affect the graph:**\n\n"
                "**Amplitude**: Height of price swings (bigger = taller waves/jumps)\n\n"
                "**Frequency**: Speed of oscillation (higher = faster waves)\n\n"
                "**Drift**: Overall trend (positive = upward, negative = downward)\n\n"
                "**Noise**: Random variation (higher = more erratic)\n\n"
                "**Data Points**: Length of simulation period")
        
        amplitude = st.slider(
            "Amplitude",
            min_value=0.1,
            max_value=2.0,
            value=st.session_state.amplitude,
            step=0.05,
            help="Controls the SIZE of price movements. 0.1 = tiny swings, 2.0 = huge swings"
        )
        
        frequency = st.slider(
            "Frequency",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.frequency,
            step=0.1,
            help="Controls SPEED of oscillation (wave pattern only). 0.1 = slow wave, 5.0 = rapid oscillations"
        )
        
        drift = st.slider(
            "Drift",
            min_value=-1.0,
            max_value=1.0,
            value=st.session_state.drift,
            step=0.05,
            help="Controls TREND direction. Negative = downtrend, 0 = neutral, Positive = uptrend"
        )
        
        st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #3a3e50;'>", unsafe_allow_html=True)
        
        noise = st.slider(
            "Noise Level",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.noise,
            step=0.05,
            help="Adds RANDOMNESS. 0 = smooth, 1 = very chaotic"
        )
        
        data_points = st.slider(
            "Data Points",
            min_value=30,
            max_value=365,
            value=st.session_state.data_points,
            step=5,
            help="Number of trading days to simulate. More days = longer time period"
        )
        
        # Check if parameters changed
        params_changed = (
            amplitude != st.session_state.amplitude or
            frequency != st.session_state.frequency or
            drift != st.session_state.drift or
            noise != st.session_state.noise or
            data_points != st.session_state.data_points
        )
        
        if params_changed:
            st.session_state.amplitude = amplitude
            st.session_state.frequency = frequency
            st.session_state.drift = drift
            st.session_state.noise = noise
            st.session_state.data_points = data_points
            # Generate new seed for different data
            st.session_state.data_seed = np.random.randint(0, 1000000)
            generate_data()
            st.rerun()
        
        st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #3a3e50;'>", unsafe_allow_html=True)
        
        if st.button("🔄 Regenerate Data", use_container_width=True):
            # Generate completely new seed for different data
            st.session_state.data_seed = np.random.randint(0, 1000000)
            generate_data()
            st.rerun()
        
        if st.button("🆕 New Session", use_container_width=True):
            st.session_state.page = 'entry'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align: center; color: #8a8697; font-size: 0.75em; border-top: 1px solid #3a3e50; padding-top: 15px;">
            Academic AI Mathematics Project © 2024
        </p>
        """, unsafe_allow_html=True)
    
    # Main content
    if st.session_state.price_data is None:
        st.session_state.data_seed = np.random.randint(0, 1000000)
        generate_data()
    
    metrics = calculate_metrics()
    
    if metrics:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            vol_level = "High" if metrics['volatility'] > 0.6 else "Moderate" if metrics['volatility'] > 0.3 else "Low"
            vol_color = "#e57373" if metrics['volatility'] > 0.6 else "#c4b5a0" if metrics['volatility'] > 0.3 else "#66bb6a"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📊 Volatility Index</div>
                <div class="metric-value" style="color: {vol_color};">{metrics['volatility']*100:.1f}%</div>
                <div class="metric-sublabel">{vol_level} volatility (↑ with amplitude & noise)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💰 Avg Price</div>
                <div class="metric-value" style="color: #5b9a8b;">${metrics['avg_price']:,.0f}</div>
                <div class="metric-sublabel">Mean value</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            trend_dir = "↑ Bullish" if metrics['slope'] > 5 else "↓ Bearish" if metrics['slope'] < -5 else "→ Neutral"
            trend_color = "#5b9a8b" if metrics['slope'] > 5 else "#e57373" if metrics['slope'] < -5 else "#c4b5a0"
            trend_val = f"+${abs(metrics['slope']):.1f}/day" if metrics['slope'] > 0 else f"-${abs(metrics['slope']):.1f}/day"
            drift_indicator = "(controlled by drift parameter)" if abs(st.session_state.drift) > 0.1 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📈 Trend</div>
                <div class="metric-value" style="color: {trend_color};">{trend_dir}</div>
                <div class="metric-sublabel">{trend_val} {drift_indicator}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            stab_label = "Stable" if metrics['stability'] > 70 else "Mixed" if metrics['stability'] > 40 else "Unstable"
            stab_color = "#66bb6a" if metrics['stability'] > 70 else "#c4b5a0" if metrics['stability'] > 40 else "#e57373"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🛡️ Stability</div>
                <div class="metric-value" style="color: {stab_color};">{metrics['stability']:.0f}%</div>
                <div class="metric-sublabel">{stab_label} market</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Price chart
        df = st.session_state.price_data
        
        # Calculate volatility zones
        returns = df['price'].pct_change().abs()
        avg_return = returns.mean()
        
        fig_price = go.Figure()
        
        # Add volatility zones
        for i in range(1, len(df)):
            if returns.iloc[i] > avg_return * 1.8:
                fig_price.add_shape(
                    type="rect",
                    x0=df.iloc[i-1]['date'],
                    x1=df.iloc[i]['date'],
                    y0=df['price'].min() * 0.97,
                    y1=df['price'].max() * 1.03,
                    fillcolor="rgba(229, 115, 115, 0.06)",
                    line_width=0,
                    layer="below"
                )
            elif returns.iloc[i] < avg_return * 0.5:
                fig_price.add_shape(
                    type="rect",
                    x0=df.iloc[i-1]['date'],
                    x1=df.iloc[i]['date'],
                    y0=df['price'].min() * 0.97,
                    y1=df['price'].max() * 1.03,
                    fillcolor="rgba(91, 154, 139, 0.06)",
                    line_width=0,
                    layer="below"
                )
        
        # Add price line
        fig_price.add_trace(go.Scatter(
            x=df['date'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color='#4a6fa5', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(74, 111, 165, 0.1)',
            hovertemplate='<b>%{x|%b %d}</b><br>Price: $%{y:,.2f}<extra></extra>'
        ))
        
        fig_price.update_layout(
            title="Price Over Time",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            template='plotly_dark',
            paper_bgcolor='#2a2d3a',
            plot_bgcolor='#2a2d3a',
            font=dict(color='#c9c5be'),
            height=400,
            margin=dict(l=60, r=30, t=60, b=60)
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        # High/Low and Volume charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # High/Low chart
            df['spread'] = df['high'] - df['low']
            avg_spread = df['spread'].mean()
            
            colors = ['rgba(229, 115, 115, 0.5)' if s > avg_spread * 1.5 else 'rgba(91, 154, 139, 0.4)' 
                     for s in df['spread']]
            
            fig_highlow = go.Figure()
            
            fig_highlow.add_trace(go.Bar(
                x=df['date'],
                y=df['high'] - df['low'],
                base=df['low'],
                name='Price Range',
                marker=dict(color=colors),
                hovertemplate='<b>%{x|%b %d}</b><br>High: $%{customdata[0]:,.2f}<br>Low: $%{customdata[1]:,.2f}<extra></extra>',
                customdata=df[['high', 'low']].values
            ))
            
            fig_highlow.add_trace(go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='markers',
                name='Price',
                marker=dict(color='#c4b5a0', size=4),
                hovertemplate='<b>%{x|%b %d}</b><br>Price: $%{y:,.2f}<extra></extra>'
            ))
            
            fig_highlow.update_layout(
                title="High vs Low Range",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode='x unified',
                template='plotly_dark',
                paper_bgcolor='#2a2d3a',
                plot_bgcolor='#2a2d3a',
                font=dict(color='#c9c5be'),
                height=350,
                showlegend=False,
                margin=dict(l=60, r=20, t=60, b=60)
            )
            
            st.plotly_chart(fig_highlow, use_container_width=True)
        
        with col_chart2:
            # Volume chart
            avg_volume = df['volume'].mean()
            colors = ['rgba(74, 111, 165, 0.7)' if v > avg_volume * 1.3 else 'rgba(91, 154, 139, 0.5)' 
                     for v in df['volume']]
            
            fig_volume = go.Figure()
            
            fig_volume.add_trace(go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                marker=dict(color=colors),
                hovertemplate='<b>%{x|%b %d}</b><br>Volume: %{y:,.0f}<extra></extra>'
            ))
            
            fig_volume.update_layout(
                title="Trading Volume",
                xaxis_title="Date",
                yaxis_title="Volume",
                hovermode='x unified',
                template='plotly_dark',
                paper_bgcolor='#2a2d3a',
                plot_bgcolor='#2a2d3a',
                font=dict(color='#c9c5be'),
                height=350,
                showlegend=False,
                margin=dict(l=60, r=20, t=60, b=60)
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
        
        # Mathematical model explanation
        st.markdown("""
        <div class="model-info">
            <h4 style="color: #c4b5a0; margin-top: 0;">💡 Mathematical Model</h4>
            <p style="margin: 10px 0;"><strong style="color: #c9c5be;">Wave:</strong> P(t) = P₀ + A·sin(2πft) + D·t + ε</p>
            <p style="margin: 10px 0;"><strong style="color: #c9c5be;">Random:</strong> P(t) = P(t-1) + D + A·N(0,1) + ε·J(t)</p>
            <p style="margin: 10px 0;"><strong style="color: #c9c5be;">Volatility:</strong> σ = std(ΔP/P) × √252</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current parameter effects
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            amp_effect = "Small" if st.session_state.amplitude < 0.5 else "Medium" if st.session_state.amplitude < 1.2 else "Large"
            amp_color = "#66bb6a" if st.session_state.amplitude < 0.5 else "#c4b5a0" if st.session_state.amplitude < 1.2 else "#e57373"
            st.markdown(f"""
            <div style="background: #2a2d3a; border: 1px solid #3a3e50; border-radius: 8px; padding: 15px; text-align: center;">
                <div style="font-size: 0.85em; color: #8a8697; margin-bottom: 5px;">Amplitude Effect</div>
                <div style="font-size: 1.5em; font-weight: bold; color: {amp_color};">{amp_effect}</div>
                <div style="font-size: 0.8em; color: #8a8697; margin-top: 5px;">Current: {st.session_state.amplitude:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_p2:
            freq_effect = "Slow" if st.session_state.frequency < 1.5 else "Medium" if st.session_state.frequency < 3.0 else "Fast"
            freq_color = "#66bb6a" if st.session_state.frequency < 1.5 else "#c4b5a0" if st.session_state.frequency < 3.0 else "#4a6fa5"
            st.markdown(f"""
            <div style="background: #2a2d3a; border: 1px solid #3a3e50; border-radius: 8px; padding: 15px; text-align: center;">
                <div style="font-size: 0.85em; color: #8a8697; margin-bottom: 5px;">Wave Speed</div>
                <div style="font-size: 1.5em; font-weight: bold; color: {freq_color};">{freq_effect}</div>
                <div style="font-size: 0.8em; color: #8a8697; margin-top: 5px;">Current: {st.session_state.frequency:.1f}x</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_p3:
            drift_effect = "Bearish" if st.session_state.drift < -0.2 else "Neutral" if st.session_state.drift < 0.2 else "Bullish"
            drift_color = "#e57373" if st.session_state.drift < -0.2 else "#c4b5a0" if st.session_state.drift < 0.2 else "#5b9a8b"
            st.markdown(f"""
            <div style="background: #2a2d3a; border: 1px solid #3a3e50; border-radius: 8px; padding: 15px; text-align: center;">
                <div style="font-size: 0.85em; color: #8a8697; margin-bottom: 5px;">Market Drift</div>
                <div style="font-size: 1.5em; font-weight: bold; color: {drift_color};">{drift_effect}</div>
                <div style="font-size: 0.8em; color: #8a8697; margin-top: 5px;">Current: {st.session_state.drift:+.2f}</div>
            </div>
            """, unsafe_allow_html=True)

# Main app routing
def main():
    if st.session_state.page == 'welcome':
        render_welcome_page()
    elif st.session_state.page == 'entry':
        render_entry_page()
    elif st.session_state.page == 'dashboard':
        render_dashboard()

if __name__ == "__main__":
    main()