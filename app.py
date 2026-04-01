import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# CSS：隱藏加減號 + 深色高對比度
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* 核心：隱藏 number_input 的加減按鈕 */
    button.step-up, button.step-down { display: none !important; }
    div[data-testid="stNumberInputStepUp"], div[data-testid="stNumberInputStepDown"] { display: none !important; }
    
    /* 讓輸入框填滿空間並美化 */
    .stNumberInput input {
        background-color: #1a1c23 !important;
        color: #00ff00 !important;
        font-size: 24px !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        text-align: center;
    }
    
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.8em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; border: none; font-size: 18px;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.4);
        margin-top: 10px;
    }
    label { color: #eee !important; font-weight: bold; font-size: 16px; margin-bottom: 5px; }
    </style>
    
    <script>
    // 強制唤起手機純數字鍵盤 (針對所有輸入框)
    var applyNumericKeyboard = function() {
        var inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(function(input) {
            input.setAttribute('inputmode', 'decimal'); // 喚起帶小數點的數字鍵盤
            input.setAttribute('pattern', '[0-9]*');
        });
    };
    setTimeout(applyNumericKeyboard, 1000);
    setInterval(applyNumericKeyboard, 3000); // 持續監控
    </script>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 2. 輸入區 (隱藏按鈕後的乾淨輸入)
c1, c2 = st.columns(2)
sid_num = c1.number_input("股票代號", value=4807, step=1)
sid = str(sid_num)
cost = c2.number_input("外資/法人成本", value=38.53, step=0.01, format="%.2f")

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
        with st.spinner('金兔正在校正數據與 K 線...'):
            name, df, price = get_data(sid)

            if price and not pd.isna(price):
                # --- 📈 1. K 線圖 (縮放優化版) ---
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20, ma60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
                    fig.update_layout(
                        xaxis_rangeslider_visible=True, xaxis_rangeslider_thickness=0.08,
                        height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10,r=10,t=10,b=10), dragmode='pan', hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    ma20, ma60 = 0, 0

                # --- 2. 邏輯判定 ---
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_bull = price > ma20 > ma60 if ma60 > 0 else False
                is_god = cost >= (price * 1.5) 
                
                strategy, color = ("📍 低價佈局期", "#51cf66") if price < cost else \
                                  (f"📍 起跑區 (看{p104})", "#fcc419") if price < p104 else \
                                  ("📍 強勢波段中", "#ff6b6b")

                # --- 3. 完整 HTML 卡片 ---
                bull_html = f'''<div style="background: linear-gradient(135deg, #fff9db, #fcc419); color: #5d4037; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid #fcc419;">🔥 偵測到「多頭線型」排列</div>''' if is_bull else ""
                god_html = f'''<div style="background: #ff8787; color: white; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold;">⚠️ 偵測到「上古神獸」<br><span style="font-size:12px;">(建議更改為「融資成本」重新分析)</span></div>''' if is_god else ""

                full_card_html = f'''
                <div style="font-family: -apple-system, sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold;">{name} ({sid})</span>
                    </div>
                    {bull_html} {god_html}
                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                    </div>
                    <div style="background: #fff5f5; border-left: 6px solid #ff6b6b; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
                        <div style="font-weight: bold; color: #ff6b6b; font-size: 16px; margin-bottom: 5px;">🐰 兔兔建議：</div>
                        <div style="font-size: 15px;">{strategy}</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 20px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td style="padding: 12px 5px;">關卡一 (1.2)</td><td style="text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">關卡二 (1.4)</td><td style="text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee; color: #cc0000;"><td style="padding: 12px 5px;">關卡三 (1.7神獸)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{t3:.2f}</td></tr>
                    </table>
                    <div style="background: #ebfbee; padding: 18px; border-radius: 15px; border: 2px dashed #2b8a3e;">
                        <div style="text-align: center; color: #2b8a3e; font-weight: bold; margin-bottom: 12px;">🐰 兔子理財：選股四原則</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 12px; color: #2b8a3e; text-align: center;">🚀 <b>優先強勢股</b></div>
                            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 12px; color: #2b8a3e; text-align: center;">🤝 <b>法人加碼</b></div>
                            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 12px; color: #2b8a3e; text-align: center;">📉 <b>多頭線型</b></div>
                            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 12px; color: #2b8a3e; text-align: center;">🎯 <b>貼近成本</b></div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=1000, scrolling=True)
            else:
                st.error("❌ 抓取數據失敗。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
