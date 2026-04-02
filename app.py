import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 格局大師", page_icon="🐰", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 25px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 22px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 格局分析儀")

# 2. 原生 HTML 九宮格輸入框 (上下排列)
query_params = st.query_params
sid_str = query_params.get("sid", "4807")
cost_str = query_params.get("cost", "38.53")

html_input_component = f"""
    <div style="font-family: -apple-system, sans-serif; padding: 10px 5px;">
        <div style="margin-bottom: 20px;">
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 16px;">股票代號</div>
            <input type="tel" id="sid_box" value="{sid_str}" inputmode="decimal" 
                style="width: 100%; height: 70px; background: #1a1c23; border: 2px solid #555; border-radius: 18px; color: #ff4b4b; font-size: 32px; text-align: center; font-weight: bold; outline: none; box-sizing: border-box;">
        </div>
        <div style="margin-bottom: 10px;">
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 16px;">外資/法人成本</div>
            <input type="tel" id="cost_box" value="{cost_str}" inputmode="decimal" 
                style="width: 100%; height: 70px; background: #1a1c23; border: 2px solid #555; border-radius: 18px; color: #ff4b4b; font-size: 32px; text-align: center; font-weight: bold; outline: none; box-sizing: border-box;">
        </div>
    </div>
    <script>
        const s = document.getElementById('sid_box');
        const c = document.getElementById('cost_box');
        function update() {{
            const url = new URL(window.parent.location);
            url.searchParams.set('sid', s.value);
            url.searchParams.set('cost', c.value);
            window.parent.history.replaceState({{}}, '', url);
        }}
        s.oninput = update; c.oninput = update; s.onblur = update; c.onblur = update;
    </script>
"""
components.html(html_input_component, height=260)

# --- 🚀 格局與型態判定邏輯 ---
def analyze_market_status(df):
    last = df.iloc[-1]
    m20 = df['MA20'].iloc[-1]
    m60 = df['MA60'].iloc[-1]
    
    # 格局判定
    if last['Close'] > m20 > m60:
        status, color, advise = "🔥 多頭格局 (強勢區)", "#fff9db", "【迎向暴漲】慣性向上，回踩不破季線即是收貨機會。"
    elif last['Close'] < m20 < m60:
        status, color, advise = "❄️ 空頭格局 (弱勢區)", "#e9ecef", "【防範暴跌】下方無支撐，1.04 突破點通常站不穩。"
    else:
        status, color, advise = "🌀 盤整格局 (整理區)", "#e3fafc", "【50% 盤整危險區】波動縮小中，別碰！等待方向明確。"
    
    # K線單棒補充 (對照圖1)
    body = abs(last['Close'] - last['Open'])
    avg_b = abs(df['Close'] - df['Open']).tail(10).mean()
    l_shadow = min(last['Close'], last['Open']) - last['Low']
    
    extra = ""
    if last['Close'] > last['Open'] and body > avg_b * 2:
        extra = "<br>🚩 偵測到「大陽線」：多方絕對優勢。"
    elif l_shadow > body * 1.5:
        extra = "<br>⚓ 偵測到「長下影線」：下方有買盤支撐。"

    return status, color, advise + extra

@st.cache_data(ttl=300)
def get_stock_data(sid):
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60:
                name = twstock.codes.get(sid).name if twstock.codes.get(sid) else sid
                price = float(df['Close'].iloc[-1])
                change = price - float(df['Close'].iloc[-2])
                return name, df, price, change
        except: continue
    return sid, pd.DataFrame(), None, 0

if st.button("🚀 執行 AI 格局大集合分析"):
    try:
        cost = float(cost_str)
        name, df, price, change = get_stock_data(sid_str)

        if price:
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean()
            m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
            
            # 格局分析
            status_title, status_bg, ai_advise = analyze_market_status(df)

            # K線圖
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="月線", line=dict(color='#f06595', width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
            fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

            # 數據精算
            p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            p_color = "#ff4d4d" if change > 0 else ("#00b050" if change < 0 else "#eee")
            
            def get_st(val):
                if price >= val: return 'color: #ff4b4b; font-weight: bold;', '🚩 已達成 '
                return 'color: #333;', ''
            s104, l104 = get_st(p104); st1, lt1 = get_st(t1); st2, lt2 = get_st(t2); st3, lt3 = get_st(t3)
            sl_row = f'''<tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 12px 5px; color: #cc0000; font-weight: bold;">風控回檔位 (-6%)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{round(p104*0.94,2)}</td></tr>''' if price >= p104 else ""

            # 渲染卡片
            full_card = f'''
            <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                    <span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span>
                </div>

                <div style="background: {status_bg}; padding: 15px; border-radius: 15px; border: 2px solid #ddd; margin-bottom: 15px; text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #333;">{status_title}</div>
                    <div style="font-size: 14px; color: #555; font-weight: bold; line-height: 1.5;">{ai_advise}</div>
                </div>

                <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{price:.2f}</div><div style="font-size:14px; color:{p_color}; font-weight:bold;">漲跌: {change:.2f}</div></div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                    <tr><td style="padding: 10px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                    <tr style="background: #fff9db;"><td style="padding: 10px 5px; color: #e67e22; font-weight: bold;">{l104}突破點 (1.04)</td><td style="text-align: right; {s104}">{p104:.2f}</td></tr>
                    {sl_row}
                    <tr><td style="padding: 10px 5px;">{lt1}目標一 (1.2)</td><td style="text-align: right; {st1}">{t1:.2f}</td></tr>
                    <tr style="background: #fafafa;"><td style="padding: 10px 5px;">{lt2}目標二 (1.4)</td><td style="text-align: right; {st2}">{t2:.2f}</td></tr>
                    <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 5px; font-weight: bold;">{lt3}目標三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right; {st3}">{t3:.2f}</td></tr>
                </table>

                <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                    <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🎯 仙兔實戰心法判定</div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">1. <b>強勢股</b>：站穩季線之上</span> <span style="font-size: 20px;">{"✅" if price > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">2. <b>法人加碼</b>：盤整區連買</span> <span style="font-size: 20px;">✅</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">3. <b>多頭型態</b>：均線排列向上</span> <span style="font-size: 20px;">{"✅" if price > m20 > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">4. <b>突破攻擊</b>：突破 1.04 點</span> <span style="font-size: 20px;">{"✅" if price >= p104 else "❌"}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''
            components.html(full_card, height=2200, scrolling=True)
    except: st.error("⚠️ 請輸入數字後點擊分析。")
