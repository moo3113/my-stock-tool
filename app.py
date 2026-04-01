import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 強制亮色模式 CSS
st.markdown("""
    <style>
    .stApp { background-color: white; }
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
            df = ticker.history(period="120d")
            if not df.empty and len(df) >= 60:
                price = float(df['Close'].iloc[-1])
                break
        except: continue
    return name, df, price

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在掃描多頭排列...'):
            name, df, price = get_data(sid)

            if price and not pd.isna(price):
                # 1. K 線圖
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20, ma60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#228be6', width=2)))
                    fig.update_layout(xaxis_rangeslider_visible=False, height=300, template="plotly_white", margin=dict(l=5,r=5,t=5,b=5))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    ma20, ma60 = 0, 0

                # 2. 邏輯判斷
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                # 多頭判定：現價 > 月線 > 季線
                is_bull = price > ma20 > ma60 if ma60 > 0 else False
                
                if price < cost: strategy, color = "📍 現價低於成本，法人收貨中。", "#51cf66"
                elif price < p104: strategy, color = f"📍 起跑區，站穩 1.04 ({p104}) 即起飛。", "#fcc419"
                else: strategy, color = "📍 強勢波段中，不建議追高。", "#ff6b6b"

                # 3. HTML 卡片渲染
                bull_html = '<div style="background: #fff9db; color: #856404; padding: 12px; margin: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #ffeeba;">🔥 偵測到「多頭線型」排列</div>' if is_bull else ""
                
                full_card = f'''
                <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 20px; border: 1px solid #eee;">
                    <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 15px; text-align: center; border-radius: 15px 15px 0 0;">
                        <span style="font-size: 22px; font-weight: bold;">{name} ({sid})</span>
                    </div>
                    {bull_html}
                    <div style="padding: 20px; text-align: center; display: flex; justify-content: space-around;">
                        <div><div style="font-size: 12px; color: #999;">現價</div><div style="font-size: 32px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                        <div><div style="font-size: 12px; color: #999;">季線</div><div style="font-size: 32px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                    </div>
                    <div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 12px; margin: 10px; border-radius: 5px;">
                        <div style="font-weight: bold; color: #ff6b6b; font-size: 14px;">🐰 兔兔建議：</div>
                        <div style="font-size: 14px; color: #333;">{strategy}</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 15px; color: #444;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 10px;">法人成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 10px; color: #e67e22;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td style="padding: 10px;">關卡一 (1.2)</td><td style="text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 10px;">關卡二 (1.4)</td><td style="text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px; color: #cc0000;">關卡三 (1.7神獸)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{t3:.2f}</td></tr>
                    </table>
                </div>
                '''
                components.html(full_card, height=650)
            else:
                st.error("❌ 抓取不到數據。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
