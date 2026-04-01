import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 介面美化
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; border: none;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

c1, c2 = st.columns(2)
sid = c1.text_input("股票代號", value="4807")
cost_str = c2.text_input("外資/法人成本", value="38.53")

# --- 核心數據抓取 (含快取機制，降低伺服器壓力) ---
@st.cache_data(ttl=600) # 10 分鐘內不重複抓取相同代號
def get_stock_all_in_one(sid):
    name, df, price = sid, pd.DataFrame(), None
    
    # A. 抓名稱
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass

    # B. 嘗試 yfinance (雙後綴嘗試)
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            tmp_df = ticker.history(period="150d")
            if not tmp_df.empty and len(tmp_df) >= 60:
                df = tmp_df
                price = float(df['Close'].iloc[-1])
                break
        except: continue
    
    # C. 備援：twstock 即時價 (解決 yfinance 斷線導致 nan)
    if price is None or pd.isna(price) or price == 0:
        try:
            rt = twstock.realtime.get(sid)
            if rt and rt['success']:
                price = float(rt['realtime']['latest_trade_price'])
        except: pass
        
    return name, df, price

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在同步全球數據...'):
            name, df, price = get_stock_all_in_one(sid)

            if price and not pd.isna(price):
                # --- 📈 1. 繪製 K 線圖 ---
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20 = df['MA20'].iloc[-1]
                    ma60 = df['MA60'].iloc[-1]
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="K線", increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線(60MA)", line=dict(color='#228be6', width=2)))
                    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(l=5, r=5, t=10, b=10), template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    ma20, ma60 = 0, 0

                # --- 🐰 2. 分析計算 ---
                p104, t1, t2 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2)
                is_bull = (price > ma20 > ma60) if ma60 > 0 else False
                
                bull_html = '<div style="background: linear-gradient(135deg, #FFF9C4, #FBC02D); color: #5D4037; padding: 12px; margin: 10px 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #FBC02D;">🔥 偵測到「多頭線型」排列</div>' if is_bull else ""
                
                if price < cost: strategy, color = "📍 現價低於成本，法人收貨中，適合低接。", "#51cf66"
                elif price < p104: strategy, color = f"📍 起跑區，站穩 1.04 ({p104}) 後即起飛。", "#fcc419"
                else: strategy, color = "📍 波段行進中，注意壓力，不建議追高。", "#ff6b6b"

                # --- 🐰 3. 渲染卡片 ---
                full_card = f'''
                <div style="font-family: sans-serif; background: #fffafb; padding: 5px;">
                    <div style="background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ffe3e3;">
                        <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold;">{name} ({sid})</div>
                        </div>
                        {bull_html}
                        <div style="padding: 25px; text-align: center;">
                            <div style="display: flex; justify-content: space-around; align-items: center;">
                                <div><div style="font-size: 12px; color: #888;">當前現價</div><div style="font-size: 42px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                                <div style="border-left: 1px solid #eee; height: 50px;"></div>
                                <div><div style="font-size: 12px; color: #888;">季線 (60MA)</div><div style="font-size: 30px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                            </div>
                        </div>
                        <div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 20px 15px 20px; border-radius: 8px;">
                            <div style="font-weight: bold; color: #ff6b6b; margin-bottom: 5px; font-size: 15px;">🐰 兔兔戰術建議：</div>
                            <div style="font-size: 14px; line-height: 1.5;">{strategy}</div>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 15px; color: #555;">
                            <tr style="background: #fafafa; border-top: 1px solid #eee;"><td style="padding: 12px 20px;">法人成本</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                            <tr style="background: #fff9db;"><td style="padding: 12px 20px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                            <tr><td style="padding: 12px 20px;">關卡一 (1.2)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                            <tr style="background: #fafafa;"><td style="padding: 12px 20px;">關卡二 (1.4)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        </table>
                    </div>
                </div>
                '''
                components.html(full_card, height=550, scrolling=True)
            else:
                st.error("❌ 伺服器忙碌中，請點擊按鈕重試或檢查代號。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
