import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from data.websocket_client import latest_orderbook, run_in_thread, get_trade_metrics
from streamlit_autorefresh import st_autorefresh
from utils.almgren_chriss import optimal_execution
import numpy as np

# Start websocket listener once
if 'ws_thread_started' not in st.session_state:
    run_in_thread()
    st.session_state.ws_thread_started = True

st.set_page_config(layout="wide")
st.title("GoQuant Real-time Trade Simulator")

# Auto-refresh every 1 second to update orderbook and metrics
st_autorefresh(interval=1000, limit=None, key="refresh")

# Layout: 3 columns with wide spacing
col1, spacer1, col2, spacer2, col3 = st.columns([1.2, 0.2, 2.4, 0.2, 1.2])

with col1:
    st.header("Input Parameters")

    exchange = st.selectbox("Exchange", ["OKX"], disabled=True)
    asset = st.selectbox("Spot Asset", ["BTC-USDT-SWAP"], disabled=True)
    order_type = st.selectbox("Order Type", ["market"], disabled=True)

    quantity = st.number_input("Quantity (USD)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
    volatility = st.slider("Volatility (%)", 0.0, 10.0, 2.5)
    fee_tier = st.selectbox("Fee Tier", ["Regular", "VIP 1", "VIP 2"])

    # Almgren-Chriss Model Parameters
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

    # Initialize figure only once and store in session state
    if 'orderbook_fig' not in st.session_state:
        fig = go.Figure()
        st.session_state.orderbook_fig = fig
    else:
        fig = st.session_state.orderbook_fig
    fig.data = []  # Clear previous traces on each update

    if orderbook:
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])

        bids_df = pd.DataFrame(bids, columns=["price", "size"]).astype(float).sort_values(by='price', ascending=False).head(20) # Limit to top bids
        asks_df = pd.DataFrame(asks, columns=["price", "size"]).astype(float).sort_values(by='price', ascending=True).head(20) # Limit to top asks

        best_bid = bids_df["price"].max() if not bids_df.empty else 0
        best_ask = asks_df["price"].min() if not asks_df.empty else 0
        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
        st.metric("Mid Price", f"{mid_price:.2f} USD")

        # Add traces for bids (green)
        fig.add_trace(go.Bar(
            x=bids_df["price"],
            y=bids_df["size"],
            name='Bids',
            marker_color='green',
            opacity=0.7
        ))

        # Add traces for asks (red)
        fig.add_trace(go.Bar(
            x=asks_df["price"],
            y=asks_df["size"],
            name='Asks',
            marker_color='red',
            opacity=0.7
        ))

        fig.update_layout(
            title="Orderbook Depth",
            xaxis_title="Price",
            yaxis_title="Size",
            barmode='group', # or 'overlay' for stacked bars
            xaxis=dict(side="left"),
            yaxis=dict(side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Display the figure with interactive features
        st.plotly_chart(fig, use_container_width=True, clear_figure=False, config={'modeBarButtonsToAdd': ['pan2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d', 'hoverClosestCartesian', 'toImage', 'autoScale2d', 'select2d', 'lasso2d']})

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
                volatility=volatility / 100.0  # Convert % to decimal
            )
    else:
        st.text("Waiting for orderbook data...")

with col3:
    st.header("Trade Simulation Metrics")

    if "latest_metrics" in st.session_state:
        metrics = st.session_state.latest_metrics

        st.metric("Expected Slippage", f"{metrics['slippage']:.4f} USD")
        st.metric("Expected Fees", f"{metrics['fees']:.4f} USD")
        st.metric("Market Impact", f"{metrics['market_impact']:.4f} USD")
        st.metric("Net Cost", f"{metrics['net_cost']:.4f} USD")
        st.metric("Maker/Taker Ratio", f"{metrics['maker_taker_ratio'] * 100:.2f}%")
        st.metric("Internal Latency", f"{metrics['latency']:.2f} ms")

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