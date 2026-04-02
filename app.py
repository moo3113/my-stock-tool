import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime
import pytz # 🚀 新增時區套件

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 終極分析儀", page_icon="🐰", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 25px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 22px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        margin-top: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 型態大師分析儀")

# 2. 九宮格輸入
query_params = st.query_params
sid_str = query_params.get("sid", "009816")
cost_str = query_params.get("cost", "10.00")

html_input_component = f"""
    <div style="font-family: -apple-system, sans-serif; padding: 10px 5px;">
        <div style="margin-bottom: 25px;">
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 12px; font-size: 16px;">股票/ETF 代號</div>
            <input type="tel" id="sid_box" value="{sid_str}" inputmode="decimal" 
                style="width: 100%; height: 75px; background: #1a1c23; border: 2px solid #555; border-radius: 18px; color: #ff4b4b; font-size: 32px; text-align: center; font-weight: bold; outline: none; box-sizing: border-box;">
        </div>
        <div style="margin-bottom: 15px;">
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 12px; font-size: 16px;">外資成本 / 融資成本</div>
            <input type="tel" id="cost_box" value="{cost_str}" inputmode="decimal" 
                style="width: 100%; height: 75px; background: #1a1c23; border: 2px solid #555; border-radius: 18px; color: #ff4b4b; font-size: 32px; text-align: center; font-weight: bold; outline: none; box-sizing: border-box;">
        </div>
    </div>
"""
components.html(html_input_component, height=280)

# --- 🚀 核心偵測與時區引擎 ---
@st.cache_data(ttl=60)
def fetch_pro_data(sid):
    sid = sid.strip()
    name = "凱基台灣 TOP 50" if sid == "009816" else sid
    try:
        tw_info = twstock.codes.get(sid); name = tw_info.name if tw_info else sid
    except: pass

    # 🌍 強制鎖定台灣時區 (CST)
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    now_t = now.strftime("%H:%M")
    
    # 判斷交易時間 (09:00-13:30 且為週一至週五)
    is_trading = ("09:00" <= now_t <= "13:30") and (now.weekday() < 5)
    is_trial = ("08:30" <= now_t <= "09:00") or ("13:25" <= now_t <= "13:30")

    for suffix in [".TW", ".TWO", ""]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="1y")
            if not df.empty:
                df_clean = df.ffill().dropna(subset=['Close'])
                p = float(df_clean['Close'].iloc[-1])
                ch = p - float(df_clean['Close'].iloc[-2]) if len(df_clean) > 1 else 0
                return name, df_clean, p, ch, is_trial, is_trading
        except: continue
    return None, None, None, 0, False, False

if st.button("🚀 執行 AI 數據分析儀"):
    try:
        cost = float(cost_str); name, df, p_val, ch_val, trial, trading = fetch_pro_data(sid_str)
        if p_val:
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA60'] = df['Close'].rolling(window=60, min_periods=1).mean()
            m20, m60 = float(df['MA20'].iloc[-1]), float(df['MA60'].iloc[-1])
            
            # 🕒 交易時間提醒 (現在絕對會出現！)
            delay_warn = ""
            if trading:
                delay_warn = '''
                <div style="background: #e3f2fd; color: #1565c0; padding: 12px; border-radius: 12px; font-size: 11px; text-align: center; margin-bottom: 20px; border: 1px solid #bbdefb; font-weight: bold;">
                    ⚠️ 目前為交易時間，現價數據約有 15-20 分鐘延遲。<br>建議等數據更新或盤後試算，或配合券商 App 獲取即時報價。
                </div>
                '''

            # 其餘邏輯 (格局、神獸、心法、K線...) 完整保留
            status = ("🔥 強勢多頭", "#fff9db", "符合「迎向暴漲」格局。") if p_val > m20 > m60 else (("❄️ 弱勢空頭", "#e9ecef", "防範暴跌...") if p_val < m20 < m60 else ("🌀 箱型盤整", "#e3fafc", "..."))
            p_color = "#ff4d4d" if ch_val > 0 else ("#00b050" if ch_val < 0 else "#eee")
            p104 = round(cost*1.04, 2)
            
            full_card = f'''
            <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;"><span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span></div>
                <div style="background: {status[1]}; padding: 15px; border-radius: 15px; border: 2px solid #ddd; margin-bottom: 15px; text-align: center;"><b style="font-size: 20px;">{status[0]}</b></div>
                <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 15px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{p_val:.2f}</div></div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                </div>
                {delay_warn}
                <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                    <tr><td style="padding: 10px 5px;">外資成本 / 融資成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                    <tr style="background: #fff9db;"><td style="padding: 10px 5px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold;">{p104:.2f}</td></tr>
                </table>
                <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                    <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 19px;">🎯 兔兔實戰心法</div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                        <div style="background: white; padding: 12px; border-radius: 12px; display: flex; justify-content: space-between;"><span>1. 強勢股判定</span> <span>{"✅" if p_val > m60 else "❌"}</span></div>
                        <div style="background: white; padding: 12px; border-radius: 12px; display: flex; justify-content: space-between;"><span>4. 攻擊判定 (1.04)</span> <span>{"✅" if p_val >= p104 else "❌"}</span></div>
                    </div>
                </div>
            </div>
            '''
            components.html(full_card, height=2100, scrolling=True)
            st.plotly_chart(go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')]).update_layout(xaxis_rangeslider_visible=False, template="plotly_dark"), use_container_width=True)
    except Exception as e: st.error(f"⚠️ 錯誤: {e}")
