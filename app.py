import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta, timezone
import pytz

# --- AUTHENTICATION & PROTOCOL CONSTANTS ---
API_KEY_1 = "goldapi-d64esmmku1ubc-io"
API_URL_2 = "https://api.gold-api.com/price/XAU"
EQUITY = 125000
RISK_PCT = 0.005 
DUBAI_TZ = pytz.timezone('Asia/Dubai')

# Sacred Windows (GMT)
SACRED_WINDOWS = [
    ("L-Window (London Open)", "07:55", "08:05"),
    ("N-Window (New York Open)", "13:25", "13:35"),
    ("T-Window (Asian Reset)", "20:55", "21:05")
]

def fetch_live_data():
    """Failover API Engine (Priority 1 -> Priority 2 -> Fallback)"""
    try:
        url = "https://www.goldapi.io/api/XAU/USD"
        headers = {"x-access-token": API_KEY_1, "Content-Type": "application/json"}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return {"price": d['price'], "source": "GoldAPI.io"}
    except: pass
    try:
        r = requests.get(API_URL_2, timeout=5)
        if r.status_code == 200:
            return {"price": r.json()['price'], "source": "Gold-API.com"}
    except: pass
    return None

def get_genesis_dna():
    """Autonomously harvests ATR, Volume Avg, and Yesterday's HI/LO"""
    try:
        gold = yf.Ticker("GC=F")
        df_h = gold.history(period="5d", interval="1h")
        df_m5 = gold.history(period="2d", interval="5m")
        hi = df_h['High'].iloc[-24:].max()
        lo = df_h['Low'].iloc[-24:].min()
        atr = (df_m5['High'] - df_m5['Low']).tail(5).mean()
        avg_vol = df_m5['Volume'].tail(21).iloc[:-1].mean()
        curr_vol = df_m5['Volume'].iloc[-1]
        velocity = (df_m5['Close'].iloc[-1] - df_m5['Close'].iloc[-6]) / atr
        return {
            "hi": hi, "lo": lo, "atr": atr, 
            "vol_pct": (curr_vol/avg_vol)*100, 
            "sent": np.clip(velocity, -1.0, 1.0),
            "m5_close": df_m5['Close'].iloc[-1],
            "m5_open": df_m5['Open'].iloc[-1],
            "m5_high": df_m5['High'].iloc[-1],
            "m5_low": df_m5['Low'].iloc[-1]
        }
    except: return None

# --- UI DESIGN ---
st.set_page_config(page_title="QUANTUM ENTANGLEMENT TERMINAL", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #00FF41; }
    h1, h2, h3, p, span, div { color: #00FF41 !important; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: #00FF41; color: black; font-weight: bold; width: 100%; height: 70px; border: none; font-size: 22px; }
    .status-box { border: 2px solid #00FF41; padding: 20px; text-align: center; background-color: #050505; }
    .price-text { font-size: 50px; font-weight: bold; text-shadow: 0 0 10px #00FF41; }
    .timer-text { font-size: 30px; color: #FF3131 !important; }
    .rule-card { border-left: 5px solid #00FF41; padding-left: 15px; margin-bottom: 20px; background: #0a0a0a; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- TIME MODULE ---
now_gmt = datetime.now(timezone.utc)
now_dubai = datetime.now(DUBAI_TZ)
mins_past_90 = (now_gmt.hour * 60 + now_gmt.minute) % 90
secs_remaining = (90 - mins_past_90) * 60 - now_gmt.second

st.title("📟 QUANTUM ENTANGLEMENT: ARCHITECT TERMINAL v12.0")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    live = fetch_live_data()
    st.markdown(f'<div class="status-box">LIVE XAUUSD PRICE<br><span class="price-text">${live["price"] if live else "OFFLINE"}</span><br><small>{live["source"] if live else ""}</small></div>', unsafe_allow_html=True)
with col_t2:
    st.markdown(f'<div class="status-box">MOC COUNTDOWN<br><span class="timer-text">{str(timedelta(seconds=secs_remaining))}</span><br><small>PHASE: {mins_past_90}m</small></div>', unsafe_allow_html=True)
with col_t3:
    st.markdown(f'<div class="status-box">DUBAI TIME (GST)<br><span class="price-text">{now_dubai.strftime("%H:%M:%S")}</span><br><small>GMT: {now_gmt.strftime("%H:%M:%S")}</small></div>', unsafe_allow_html=True)

# --- UNDERSTANDING RULES (The Mechanism) ---
with st.sidebar:
    st.header("⚙️ THE MECHANISM")
    st.markdown("""
    **RULE 1: TEMPORAL LOCK**
    Algorithms only "entangle" during Sacred Windows. Outside these times, price is 85% random noise.
    
    **RULE 2: ALGORITHMIC MASS**
    Volume must spike >150%. This proves the "Big Three" market-makers (Alpha, Beta, Gamma) are active.
    
    **RULE 3: LIQUIDITY PROBE**
    A wick MUST breach yesterday's HI or LO. Without a "Stop Hunt," there is no Liquidity Cascade.
    
    **RULE 4: BINARY CERTAINTY**
    If the DNA scan fails, the system blocks the trade. This is a **Safety Lock**, not an error.
    """)

if st.button("EXECUTE QUANTUM DNA SCAN"):
    with st.spinner('Synchronizing Wavefunction...'):
        dna = get_genesis_dna()
        if live and dna:
            # 1. Temporal Gene Check
            curr_str = now_gmt.strftime("%H:%M")
            in_window = any(start <= curr_str <= end for _, start, end in SACRED_WINDOWS)
            
            # 2. Volume Spike
            vol_pass = dna['vol_pct'] > 150
            
            # 3. Sentiment Helix
            body_size = abs(dna['m5_close'] - dna['m5_open'])
            sent_pass = body_size > (0.382 * dna['atr']) and abs(dna['sent']) > 0.40
            
            # 4. Liquidity Codon
            wick_low_dist = (dna['lo'] - dna['m5_low']) / dna['atr']
            wick_high_dist = (dna['m5_high'] - dna['hi']) / dna['atr']
            is_probed = (0.8 <= wick_low_dist <= 1.2) or (0.8 <= wick_high_dist <= 1.2)
            
            st.subheader("🕵️ ARCHITECT'S DIAGNOSTIC HUB")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.write(f"**1. Temporal Gene:** {'✅ LOCKED' if in_window else '❌ DECOHERENT'}")
                if not in_window: st.caption("Market is currently in 'Random Noise' phase. Wait for MOC Singularity.")
                
                st.write(f"**2. Volume Allele:** {'✅ PASS' if vol_pass else '❌ INSUFFICIENT'}")
                if not vol_pass: st.caption(f"Current Volume: {dna['vol_pct']:.1f}%. Need >150% for Algorithmic Mass.")
                
            with col_d2:
                st.write(f"**3. Sentiment Helix:** {'✅ PASS' if sent_pass else '❌ NO BIAS'}")
                if not sent_pass: st.caption("Candle body is too small. No clear institutional direction detected.")
                
                st.write(f"**4. Liquidity Codon:** {'✅ PROBED' if is_probed else '❌ SCANNING'}")
                if not is_probed: st.caption("Price has not touched yesterday's Stop-Loss clusters yet.")

            if in_window and vol_pass and sent_pass and is_probed:
                direction = "LONG" if dna['sent'] > 0 else "SHORT"
                entry = dna['m5_close'] - (0.2 * dna['atr']) if direction == "LONG" else dna['m5_close'] + (0.2 * dna['atr'])
                sl = entry - (1.8 * dna['atr']) if direction == "LONG" else entry + (1.8 * dna['atr'])
                tp = entry + (2.2 * (entry - sl)) if direction == "LONG" else entry - (2.2 * (sl - entry))
                lots = (EQUITY * RISK_PCT) / (1.8 * dna['atr'] * 10)
                
                st.success("💎 PHOTON_LOCKED: THE WAVEFUNCTION HAS COLLAPSED.")
                st.code(f"""
DIRECTION: MANDATORY {direction}
ENTRY:     ${entry:.2f} (Limit Order)
STOP LOSS: ${sl:.2f}
TARGET:    ${tp:.2f}
SIZE:      {lots:.2f} Lots
                """)
            else:
                st.warning("⚠️ STATUS: DECOHERENT NOISE. No Genesis Candle detected in this slice.")

st.subheader("📊 DUBAI SIGNAL LOG")
if 'log' not in st.session_state: st.session_state.log = []
if st.session_state.log:
    st.table(pd.DataFrame(st.session_state.log).tail(5))
else:
    st.write("Waiting for next Sacred Window...")

with st.expander("📚 THE QUANTUM BIBLE (Guide & Logic)"):
    st.markdown("""
    ### Why this data matters:
    1. **Live Feed:** Prioritized multi-API failover for institutional tick precision.
    2. **ATR (5m):** Used to calculate the surgical 1.8x 'Stop Hunt' buffer.
    3. **Volume Z-Score:** Ensures you only enter when the banks are active.
    4. **Dubai Time:** Synchronized with the global trading centers.
    
    ### How to Trade:
    - If Diagnostic shows **✅** on all 4, execute the limit order immediately.
    - If any **❌** appears, do not move. You are protecting your $125k capital from randomness.
    """)
