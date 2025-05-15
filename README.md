# GoQuant Real-time Trade Simulator 📈

A real-time, high-performance trade simulator built using **Streamlit**, **Plotly**, and **WebSocket integration** with the **OKX Exchange**.

🚀 **[Live Demo](https://prasad26-cse-assignment-goquant-app-wu9e9s.streamlit.app/)**

This tool provides a live view of the orderbook and simulates trade execution using market models including:
- Slippage & Market Impact Modeling
- Trade Cost Analysis
- Maker/Taker Fee Classification
- Optimal Execution using the **Almgren-Chriss** Model

---

## 🔧 Features

- 📡 **Real-time Orderbook Visualization** (via WebSocket from OKX)
- 📊 **Live Trade Execution Metrics** (slippage, fees, market impact)
- 🧠 **Almgren-Chriss Model** for optimal execution strategy
- 📈 **Plotly Charts** with smooth auto-refresh
- 💡 Fully interactive Streamlit UI

---

## 📸 Screenshots

| Live Orderbook | Execution Metrics |
|----------------|-------------------|
| ![orderbook](![image](https://github.com/user-attachments/assets/79a561d7-1d7a-468d-8a4c-0a1e821f39a0)
) | ![metrics](![image](https://github.com/user-attachments/assets/6a56aeb6-9c8b-48df-a165-3b7f3875fcad)
) |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/goquant-trade-simulator.git
cd goquant-trade-simulator
```
## 2. Create & Activate Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
# 3. Install Dependencies
```
pip install -r requirements.txt
```
# 4. Run the Application
```
streamlit run app.py
```
## 🧠 Models Used

- **Almgren-Chriss Optimal Execution**  
  - Minimizes cost and risk for splitting trades over time  
  - Uses time discretization  
  - Incorporates volatility estimates  
  - Models temporary and permanent market impacts  

- **Regression-Based Slippage Estimation**  
  - Computes expected slippage per trade volume  
  - Classifies trades as Maker or Taker based on fee tier and timing  


## 📈 Metrics Computed

- Expected Slippage  
- Expected Fees (based on OKX fee tiers)  
- Market Impact  
- Net Trading Cost  
- Maker/Taker Ratio  
- Internal Latency (ms)  


## 📚 References

- Almgren, R., & Chriss, N. (2000). *Optimal execution of portfolio transactions.*  
- OKX API Docs: [https://www.okx.com/docs-v5/en/](https://www.okx.com/docs-v5/en/)  


## 🧑‍💻 Author

**Prasad Kabade**  
B.Tech CSE | Machine Learning & Frontend Developer  
[LinkedIn](https://www.linkedin.com/in/prasadkabade) | [GitHub](https://github.com/prasadkabade)

