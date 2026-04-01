import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# CSS 美化：回歸深色高質感背景，並確保按鈕亮眼
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; border: none;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.4);
    }
    .stTextInput>div>div>input { background-color: #1a1c23; color: white; border: 1px solid #333; }
    label { color: #eee !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

c1, c2 = st.columns(2)
sid = c1.text_input("股票代號", value="4807")
cost_str = c2.text_input("外資/法人成本", value="38.53")

@st.cache_data(ttl=300)
def get_data(sid):
    name, df, price = sid, pd.DataFrame(), None
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60:
                price = float(df['Close'].iloc[-1])
                break
        except: continue
    return name, df, price

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在搬運大數據...'):
            name, df, price = get_data(sid)

            if price and not pd.isna(price):
                # --- 1. K 線圖 (Plotly 內建深色適配) ---
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20, ma60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
                    fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", 
                                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      margin=dict(l=10,r=10,t=10,b=10))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    ma20, ma60 = 0, 0

                # --- 2. 數據邏輯判斷 ---
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_bull = price > ma20 > ma60 if ma60 > 0 else False
                is_god = cost >= (price * 1.7)
                
                if price < cost: strategy, color = "📍 現價低於成本，法人收貨中。", "#51cf66"
                elif price < p104: strategy, color = f"📍 起跑區，站穩 1.04 ({p104}) 後起飛。", "#fcc419"
                else: strategy, color = "📍 波段強勢行進中，注意 1.4 壓力點。", "#ff6b6b"

                # --- 3. HTML 渲染 (找回所有遺失組件) ---
                bull_html = '<div style="background: linear-gradient(135deg, #fff9db, #fcc419); color: #5d4037; padding: 12px; margin: 10px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid #fcc419;">🔥 偵測到「多頭線型」排列</div>' if is_bull else ""
                god_html = '<div style="background: #ff8787; color: white; padding: 10px; margin: 10px; border-radius: 10px; text-align: center; font-weight: bold;">⚠️ 偵測到「上古神獸」建議換成本</div>' if is_god else ""

                full_card = f'''
                <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 20px; color: #333;">
                    <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 15px; text-align: center; border-radius: 15px;">
                        <span style="font-size: 22px; font-weight: bold;">{name} ({sid})</span>
                    </div>
                    {bull_html} {god_html}
                    <div style="padding: 20px; text-align: center; display: flex; justify-content: space-around;">
                        <div><div style="font-size: 12px; color: #999;">現價</div><div style="font-size: 36px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                        <div style="border-left: 1px solid #eee;"></div>
                        <div><div style="font-size: 12px; color: #999;">季線</div><div style="font-size: 30px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                    </div>
                    <div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 12px; margin: 0 10px 15px 10px; border-radius: 5px;">
                        <div style="font-weight: bold; color: #ff6b6b; font-size: 14px;">🐰 兔兔建議：</div>
                        <div style="font-size: 14px;">{strategy}</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 10px;">法人成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 10px; color: #e67e22;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td style="padding: 10px;">關卡一 (1.2)</td><td style="text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 10px;">關卡二 (1.4)</td><td style="text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee; color: #cc0000;"><td style="padding: 10px;">關卡三 (1.7神獸)</td><td style="text-align: right; font-weight: bold;">{t3:.2f}</td></tr>
                    </table>
                    <div style="background: #ebfbee; padding: 15px; margin-top: 15px; border-radius: 12px; border: 1px dashed #2b8a3e;">
                        <div style="text-align: center; color: #2b8a3e; font-weight: bold; margin-bottom: 10px;">🐰 兔子理財：選股四原則</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px; color: #2b8a3e;">
                            <div style="background: white; padding: 5px; border-radius: 5px;">🚀 <b>優先強勢股</b></div>
                            <div style="background: white; padding: 5px; border-radius: 5px;">🤝 <b>法人持續加碼</b></div>
                            <div style="background: white; padding: 5px; border-radius: 5px;">📉 <b>確認多頭線型</b></div>
                            <div style="background: white; padding: 5px; border-radius: 5px;">🎯 <b>現價離成本近</b></div>
                        </div>
                    </div>
                </div>
                '''
                # 這裡高度設為 850，確保所有內容（包含四原則）都能完整顯示
                components.html(full_card, height=850, scrolling=True)
            else:
                st.error("❌ 抓取不到報價，請檢查代號。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
