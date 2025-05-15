import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from data.websocket_client import latest_orderbook, run_in_thread, get_trade_metrics
from streamlit_autorefresh import st_autorefresh
from utils.almgren_chriss import optimal_execution
import datetime

# Start websocket listener once
if 'ws_thread_started' not in st.session_state:
    run_in_thread()
    st.session_state.ws_thread_started = True

st.set_page_config(layout="wide")
st.title("GoQuant Real-time Trade Simulator")

# Auto-refresh every 1 second to update orderbook and metrics
st_autorefresh(interval=1000, limit=None, key="refresh")

# Layout: 3 columns
col1, spacer1, col2, spacer2, col3 = st.columns([1.2, 0.2, 2.4, 0.2, 1.2])

# Add a header section for the date and time
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
with header_col2:
    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"<h3 style='text-align: center;'>{date_time_str}</h3>", unsafe_allow_html=True)

with col1:
    st.header("Input Parameters")
    exchange = st.selectbox("Exchange", ["OKX"], disabled=True)
    asset = st.selectbox("Spot Asset", ["BTC-USDT-SWAP"], disabled=True)
    order_type = st.selectbox("Order Type", ["market"], disabled=True)

    quantity = st.number_input("Quantity (USD)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
    volatility = st.slider("Volatility (%)", 0.0, 10.0, 2.5)
    fee_tier = st.selectbox("Fee Tier", ["Regular", "VIP 1", "VIP 2"])

    st.subheader("Execution Model Parameters")
    time_steps = st.slider("Time Steps", min_value=5, max_value=100, value=50)
    risk_aversion = st.slider("Risk Aversion", min_value=0.0001, max_value=0.01, value=0.001)
    alpha = st.slider("Temporary Impact Exponent (α)", 0.5, 2.0, 1.0)
    beta = st.slider("Permanent Impact Exponent (β)", 0.5, 2.0, 1.0)
    gamma = st.slider("Permanent Impact Coefficient (γ)", 0.01, 0.2, 0.05)
    eta = st.slider("Temporary Impact Coefficient (η)", 0.01, 0.2, 0.05)

    simulate_btn = st.button("Simulate Trade")

with col2:
    st.header("Processed Output")

    orderbook = latest_orderbook

    if 'candlestick_data' not in st.session_state:
        st.session_state.candlestick_data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close'])
        st.session_state.current_candle = {
            'time': None,
            'open': None,
            'high': None,
            'low': None,
            'close': None,
        }

    if orderbook:
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])

        bids_df = pd.DataFrame(bids, columns=["price", "size"]).astype(float)
        asks_df = pd.DataFrame(asks, columns=["price", "size"]).astype(float)

        best_bid = bids_df["price"].max() if not bids_df.empty else 0
        best_ask = asks_df["price"].min() if not asks_df.empty else 0
        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
        st.metric("Mid Price", f"{mid_price:.2f} USD")
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        if st.session_state.current_candle['time'] is None:
            st.session_state.current_candle = {
                'time': current_time,
                'open': mid_price,
                'high': mid_price,
                'low': mid_price,
                'close': mid_price,
            }
        else:
            st.session_state.current_candle['high'] = max(st.session_state.current_candle['high'], mid_price)
            st.session_state.current_candle['low'] = min(st.session_state.current_candle['low'], mid_price)
            st.session_state.current_candle['close'] = mid_price

        if current_time[-2:] != st.session_state.current_candle['time'][-2:]:
            new_candle_data = pd.DataFrame([st.session_state.current_candle])
            st.session_state.candlestick_data = pd.concat([st.session_state.candlestick_data, new_candle_data],
                                                          ignore_index=True)
            st.session_state.current_candle = {
                'time': current_time,
                'open': mid_price,
                'high': mid_price,
                'low': mid_price,
                'close': mid_price,
            }

        fig = go.Figure(data=[go.Candlestick(
            x=st.session_state.candlestick_data['time'],
            open=st.session_state.candlestick_data['open'],
            high=st.session_state.candlestick_data['high'],
            low=st.session_state.candlestick_data['low'],
            close=st.session_state.candlestick_data['close'],
            name='Price',
            increasing=dict(line=dict(color='#069039', width=1), fillcolor='#069039'),
            decreasing=dict(line=dict(color='#CE2121', width=1), fillcolor='#CE2121'),
        )])

        fig.update_layout(
            title="Candlestick Chart",
            yaxis_title="Price (USD)",
            xaxis_title="Time",
            xaxis_showgrid=False,
            yaxis_showgrid=True,
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            font=dict(family="Arial, sans-serif", size=10, color="#333"),
        )
        fig.update_yaxes(gridcolor="#e0e0e0", zerolinecolor="#999", tickformat='.2f')
        fig.update_xaxes(tickangle=-45, gridcolor="#e0e0e0", zerolinecolor="#999")

        st.plotly_chart(fig, use_container_width=True, clear_figure=False)

        if simulate_btn:
            st.session_state.latest_metrics = get_trade_metrics(orderbook, quantity, volatility, fee_tier)
            st.session_state.execution_result = optimal_execution(
                time_steps=time_steps,
                total_shares=int(quantity),
                risk_aversion=risk_aversion,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                eta=eta,
                volatility=volatility / 100.0
            )
    else:
        st.text("Waiting for orderbook data...")

with col3:
    st.header("Trade Simulation Metrics")

    if "latest_metrics" in st.session_state:
        metrics = st.session_state.latest_metrics

        slippage = metrics['slippage']
        fees = metrics['fees']
        market_impact = metrics['market_impact']
        net_cost = metrics['net_cost']

        st.metric("Expected Slippage", f"{slippage:.4f} USD")
        st.metric("Expected Fees", f"{fees:.4f} USD")
        st.metric("Market Impact", f"{market_impact:.4f} USD")
        st.metric("Net Cost", f"{net_cost:.4f} USD")
        st.metric("Maker/Taker Ratio", f"{metrics['maker_taker_ratio'] * 100:.2f}%")
        st.metric("Internal Latency", f"{metrics['latency']:.2f} ms")

        # Pie chart for slippage, fees, market impact
        pie_labels = ['Slippage', 'Fees', 'Market Impact']
        pie_values = [slippage, fees, market_impact]

        pie_fig = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_values,
            textinfo='label+percent',
            hole=0.4
        )])

        pie_fig.update_layout(title="Cost Breakdown Pie Chart")
        st.plotly_chart(pie_fig, use_container_width=True)

    if "execution_result" in st.session_state:
        st.subheader("Optimal Execution Trajectory")
        _, _, inventory_path, optimal_trajectory = st.session_state.execution_result

        execution_df = pd.DataFrame({
            "Time Step": list(range(1, len(optimal_trajectory) + 1)),
            "Shares Executed": optimal_trajectory
        })

        st.line_chart(execution_df.set_index("Time Step"))
        st.dataframe(execution_df)

# Optional: CSS Fade-in animation
st.markdown("""
    <style>
        .element-container {
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            0% {opacity: 0; transform: translateY(20px);}
            100% {opacity: 1; transform: translateY(0);}
        }
    </style>
""", unsafe_allow_html=True)

st.caption("Powered by GoQuant | Real-time Trade Execution Metrics")
