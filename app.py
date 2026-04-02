import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

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

# 2. 原生 HTML 九宮格輸入組件 (上下排列)
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
components.html(html_input_component, height=280)

# --- 🚀 核心偵測與視覺建議引擎 ---
def get_visual_advise(df):
    last = df.iloc[-1]; prev = df.iloc[-2]
    body = abs(last['Close'] - last['Open']); avg_b = abs(df['Close'] - df['Open']).tail(10).mean()
    l_shadow = min(last['Close'], last['Open']) - last['Low']
    advise = []
    if last['Close'] > last['Open'] and body > avg_b * 1.8: advise.append("🕯️ 【大陽線】多方絕對優勢，迎向暴漲！")
    if l_shadow > body * 1.5: advise.append("⚓ 【長下影線】下方支撐極強，一方有希望。")
    if last['Close'] > prev['Close'] > df.iloc[-3]['Close']: advise.append("📈 【上升慣性】暴漲機率 80%↑，建議買入警告。")
    elif last['Close'] < prev['Close'] < df.iloc[-3]['Close']: advise.append("🚨 【防範暴跌】下跌旗形出現，賣出警告 100%。")
    std = df['Close'].tail(10).std()
    if std < (last['Close'] * 0.015): advise.append("📦 【50% 盤整區】危險別碰！等待方向明確。")
    return advise

@st.cache_data(ttl=300)
def get_data(sid):
    sid = sid.strip()
    for suffix in [".TW", ".TWO", ""]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty:
                try: 
                    name = ticker.info.get('shortName', ticker.info.get('longName', sid))
                    if sid == "009816": name = "凱基台灣 TOP 50"
                except: name = sid
                return name, df, float(df['Close'].iloc[-1]), float(df['Close'].iloc[-1]) - float(df['Close'].iloc[-2])
        except: continue
    return None, None, None, 0

if st.button("🚀 執行 AI 數據大集合分析"):
    try:
        cost = float(cost_str); name, df, price, change = get_data(sid_str)
        if price:
            df['MA20'] = df['Close'].rolling(20).mean(); df['MA60'] = df['Close'].rolling(60).mean()
            m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
            
            # 1. 格局判定
            if price > m20 > m60: status = ("🔥 強勢多頭", "#fff9db", "符合「迎向暴漲」格局。")
            elif price < m20 < m60: status = ("❄️ 弱勢空頭", "#e9ecef", "防範暴跌，突破點站不穩。")
            else: status = ("🌀 箱型盤整", "#e3fafc", "50% 盤整區，別碰。")

            # 2. 🚨 神獸判定 (修正：當現價 > 外資成本 1.7 倍)
            is_god = price >= (cost * 1.7)
            god_html = f'''<div style="background: #ff4b4b; color: white; padding: 15px; margin-bottom: 15px; border-radius: 15px; text-align: center; font-weight: bold; border: 3px solid white; animation: blink 1s infinite;">⚠️ 偵測到「上古神獸」格局<br><span style="font-size:13px; font-weight:normal;">現價已超過外資成本 1.7 倍，數據參考價值下降，建議改用「融資成本」重新計算。</span></div>''' if is_god else ""

            # 3. K 線圖
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
            fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

            # 4. 數據渲染
            p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            p_color = "#ff4d4d" if change > 0 else ("#00b050" if change < 0 else "#eee")
            def get_st(val):
                if price >= val: return 'color: #ff4d4d; font-weight: bold;', '🚩 已達成 '
                return 'color: #333;', ''
            s104, l104 = get_st(p104); st1, lt1 = get_st(t1); st2, lt2 = get_st(t2); st3, lt3 = get_st(t3)
            ai_vis = get_visual_advise(df); vw_html = "".join([f'<div style="margin-bottom:6px;">{w}</div>' for w in ai_vis])

            full_card = f'''
            <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                    <span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span>
                </div>
                {god_html}
                <div style="background: {status[1]}; padding: 15px; border-radius: 15px; border: 2px solid #ddd; margin-bottom: 15px; text-align: center;">
                    <b style="font-size: 20px; color: #333;">{status[0]}</b><br>
                    <div style="font-size: 14px; color: #555; font-weight: bold; margin-top: 5px;">{status[2]}</div>
                    <div style="text-align: left; font-size: 13px; color: #444; margin-top: 10px; background: rgba(255,255,255,0.6); padding: 10px; border-radius: 8px;">{vw_html}</div>
                </div>
                <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{price:.2f}</div><div style="font-size:14px; color:{p_color}; font-weight:bold;">漲跌: {change:.2f}</div></div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                    <tr><td style="padding: 10px 5px;">外資成本 / 融資成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                    <tr style="background: #fff9db;"><td style="padding: 10px 5px; color: #e67e22; font-weight: bold;">{l104}突破點 (1.04)</td><td style="text-align: right; {s104}">{p104:.2f}</td></tr>
                    <tr><td style="padding: 10px 5px;">{lt1}目標一 (1.2)</td><td style="text-align: right; {st1}">{t1:.2f}</td></tr>
                    <tr style="background: #fafafa;"><td style="padding: 10px 5px;">{lt2}目標二 (1.4)</td><td style="text-align: right; {st2}">{t2:.2f}</td></tr>
                    <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 5px; font-weight: bold;">{lt3}目標三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right; {st3}">{t3:.2f}</td></tr>
                </table>
                <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                    <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 19px;">🎯 仙兔實戰心法審核</div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">1. <b>趨勢強勢</b>：站穩季線之上</span> <span style="font-size: 20px;">{"✅" if price > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">2. <b>多頭排列</b>：現價>月線>季線</span> <span style="font-size: 20px;">{"✅" if price > m20 > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">3. <b>突破攻擊</b>：突破成本 1.04 點</span> <span style="font-size: 20px;">{"✅" if price >= p104 else "❌"}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''
            components.html(full_card, height=2100, scrolling=True)
        else: st.error("❌ 找不到數據。")
    except: st.error("⚠️ 請輸入正確的代號與數字。")
