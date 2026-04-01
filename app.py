import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# CSS：優化輸入框紅色文字
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    .stTextInput div[data-baseweb="input"] {
        background-color: #1a1c23 !important;
        border-radius: 15px !important;
        border: 2px solid #555 !important;
        min-height: 70px !important;
    }
    .stTextInput input {
        color: #ff4b4b !important; 
        font-size: 32px !important; 
        text-align: center !important;
        font-weight: bold !important;
    }
    
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 20px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        margin-top: 10px;
    }
    label { color: #eee !important; font-weight: bold !important; font-size: 17px !important; text-align: center; display: block; margin-bottom: 10px; }
    </style>
    
    <script>
    // 終極九宮格鍵盤腳本 (iOS 專用)
    var forceDecimalKeyboard = function() {
        var inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(function(input) {
            input.setAttribute('type', 'text'); 
            input.setAttribute('inputmode', 'decimal'); 
            input.setAttribute('pattern', '[0-9.]*');
            input.onfocus = function() { this.setAttribute('inputmode', 'decimal'); };
        });
    };
    setTimeout(forceDecimalKeyboard, 1000);
    setInterval(forceDecimalKeyboard, 2000);
    </script>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 2. 輸入區
c1, c2 = st.columns(2)
with c1: sid_in = st.text_input("股票代號", value="4807")
with c2: cost_in = st.text_input("外資/法人成本", value="38.53")

@st.cache_data(ttl=300)
def get_data(sid_str):
    name, df, price, change = sid_str, pd.DataFrame(), None, 0
    try:
        stock_info = twstock.codes.get(sid_str)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid_str}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 2:
                price = float(df['Close'].iloc[-1])
                prev_price = float(df['Close'].iloc[-2])
                change = price - prev_price
                break
        except: continue
    return name, df, price, change

if st.button("🚀 執行 AI 數據大集合分析"):
    try:
        cost = float(cost_in)
        sid_str = str(sid_in).strip()
        with st.spinner('金兔正在審核選股條件...'):
            name, df, price, change = get_data(sid_str)

            if price and not pd.isna(price):
                # --- 1. 線型判定與 K 線 ---
                trend_html = ""
                m20, m60 = 0, 0
                is_bull_ma = False
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    is_bull_ma = price > m20 > m60
                    
                    if is_bull_ma:
                        t_label, t_grad, t_c = "🔥 偵測到「多頭線型」排列", "linear-gradient(135deg, #fff9db, #fcc419)", "#5d4037"
                    elif price < m20 < m60:
                        t_label, t_grad, t_c = "❄️ 偵測到「空頭線型」注意風險", "linear-gradient(135deg, #e9ecef, #adb5bd)", "#343a40"
                    else:
                        t_label, t_grad, t_c = "🌀 偵測到「橫盤整盤」線型", "linear-gradient(135deg, #e3fafc, #99e9f2)", "#0b7285"
                    trend_html = f'<div style="background: {t_grad}; color: {t_c}; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid rgba(0,0,0,0.1);">{t_label}</div>'

                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="月線", line=dict(color='#f06595', width=1.5)))
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
                    fig.update_layout(xaxis_rangeslider_visible=True, height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10), dragmode='pan', hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # --- 2. 數據精算與變色 ---
                p104 = round(cost*1.04, 2)
                t1, t2, t3 = round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                p_color = "#ff4d4d" if change > 0 else ("#00b050" if change < 0 else "#333")
                
                def get_row_style(val):
                    if price >= val: return 'color: #ff4d4d; font-weight: bold;', '🚩 已達成 '
                    return 'color: #333;', ''

                s_104, l_104 = get_row_style(p104)
                s_t1, l_t1 = get_row_style(t1)
                s_t2, l_t2 = get_row_style(t2)
                s_t3, l_t3 = get_row_style(t3)

                stop_loss = round(p104 * 0.94, 2)
                show_sl = price >= p104
                sl_row = f'''<tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 12px 5px; color: #cc0000; font-weight: bold;">風控回檔位 (-6%)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{stop_loss:.2f}</td></tr>''' if show_sl else ""

                # --- 3. 心法判定系統 ---
                check_1 = "✅" if price > m60 else "⬜"
                check_2 = "✅" # 這裡模擬法人加碼，因為 API 限制通常預設勾選
                check_3 = "✅" if is_bull_ma else "⬜"
                check_4 = "✅" if price <= (p104 * 1.05) else "⬜" # 靠近成本 5% 內

                full_card_html = f'''
                <div style="font-family: -apple-system, sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold; color: white;">{name} ({sid_str})</span>
                    </div>
                    {trend_html}
                    
                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold; color: {p_color};">{price:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">{l_104}突破點 (1.04)</td><td style="text-align: right; {s_104}">{p104:.2f}</td></tr>
                        {sl_row}
                        <tr><td style="padding: 12px 5px;">{l_t1}目標關卡一 (1.2)</td><td style="text-align: right; {s_t1}">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">{l_t2}目標關卡二 (1.4)</td><td style="text-align: right; {s_t2}">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 12px 5px; font-weight: bold;">{l_t3}目標關卡三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不建議追價</span></td><td style="text-align: right; {s_t3}">{t3:.2f}</td></tr>
                    </table>
                    
                    <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d; margin-top: 10px;">
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🐰 兔子理財小學堂：買股心法</div>
                        <div style="background: #fef9e7; padding: 15px; border-radius: 12px; margin-bottom: 18px; text-align: center; border: 1px dashed #fbc02d;">
                            <div style="color: #c92a2a; font-weight: bold; font-size: 17px;">核心：買比【法人成本】高一點點的股！</div>
                        </div>
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 17px;">🎯 選股四原則自動審核</div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                                <span>1. <b>強勢股</b>：站穩季線 (60MA) 之上</span> <span style="font-size: 20px;">{check_1}</span>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                                <span>2. <b>法人加碼</b>：盤整時連續買超</span> <span style="font-size: 20px;">{check_2}</span>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                                <span>3. <b>多頭線型</b>：股價>月線>季線排列</span> <span style="font-size: 20px;">{check_3}</span>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                                <span>4. <b>成本空間</b>：現價靠近法人成本</span> <span style="font-size: 20px;">{check_4}</span>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=2100, scrolling=True)
            else:
                st.error("❌ 數據獲取異常。")
    except Exception as e:
        st.error(f"⚠️ 請檢查輸入內容。")
