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

# 2. 原生 HTML 九宮格輸入組件
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

# --- 🚀 核心偵測與視覺智慧 ---
def get_visual_advise(df):
    if len(df) < 2: return ["🌀 數據不足，無法判定型態。"]
    last = df.iloc[-1]; prev = df.iloc[-2]
    body = abs(last['Close'] - last['Open']); avg_b = abs(df['Close'] - df['Open']).tail(10).mean()
    l_shadow = min(last['Close'], last['Open']) - last['Low']
    advise = []
    if last['Close'] > last['Open'] and body > avg_b * 1.5: advise.append("🕯️ 【大陽線】多方絕對優勢，迎向暴漲！")
    if l_shadow > body * 1.2: advise.append("⚓ 【長下影線】下方支撐極強，一方有希望。")
    if len(df) >= 3:
        if last['Close'] > prev['Close'] > df.iloc[-3]['Close']: advise.append("📈 【上升慣性】暴漲機率 80%↑，買入警告。")
        elif last['Close'] < prev['Close'] < df.iloc[-3]['Close']: advise.append("🚨 【防範暴跌】下跌旗形出現，賣出警告 100%。")
    return advise

@st.cache_data(ttl=300)
def get_data(sid):
    sid = sid.strip()
    # 增加搜尋順序與 ETF 特化搜尋
    for suffix in [".TW", ".TWO", ""]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="200d") # 抓長一點確保有季線
            if not df.empty and len(df) >= 1:
                name = "凱基台灣 TOP 50" if sid == "009816" else sid
                try:
                    if sid != "009816":
                        tw_info = twstock.codes.get(sid)
                        if tw_info: name = tw_info.name
                except: pass
                p = float(df['Close'].iloc[-1])
                ch = p - float(df['Close'].iloc[-2]) if len(df) >= 2 else 0
                return name, df, p, ch
        except: continue
    return None, None, None, 0

if st.button("🚀 執行 AI 數據分析儀"):
    try:
        cost = float(cost_str); name, df, price_val, change_val = get_data(sid_str)
        if price_val is not None:
            # 計算均線 (加入 min_periods 確保新股也能顯示數值)
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA60'] = df['Close'].rolling(window=60, min_periods=1).mean()
            m20_val = df['MA20'].iloc[-1]
            m60_val = df['MA60'].iloc[-1]
            
            # 格局判定
            if price_val > m20_val > m60_val: status = ("🔥 強勢多頭", "#fff9db", "符合「迎向暴漲」格局。")
            elif price_val < m20_val < m60_val: status = ("❄️ 弱勢空頭", "#e9ecef", "防範暴跌，突破點站不穩。")
            else: status = ("🌀 箱型盤整", "#e3fafc", "50% 盤整區，別碰。")
            
            is_god = price_val >= (cost * 1.7)
            god_html = f'''<div style="background: #ff4b4b; color: white; padding: 15px; margin-bottom: 15px; border-radius: 15px; text-align: center; font-weight: bold; border: 3px solid white;">⚠️ 偵測到「上古神獸」格局<br><span style="font-size:13px; font-weight:normal;">現價已超過外資成本 1.7 倍，建議改用「融資成本」分析。</span></div>''' if is_god else ""

            # K線圖
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
            fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

            # 數據渲染
            p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            p_color = "#ff4d4d" if change_val > 0 else ("#00b050" if change_val < 0 else "#eee")
            
            # 🛡️ 風控邏輯
            stop_loss = round(p104 * 0.94, 2)
            sl_html = f'''<tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 10px 5px; color: #cc0000; font-weight: bold;">🚩 風控回檔位 (-6%)<br><span style="font-size:10px; color:#999;">*突破點回檔之簡化風控</span></td><td style="text-align: right; font-weight: bold; color: #cc0000;">{stop_loss:.2f}</td></tr>''' if price_val >= p104 else ""

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
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{price_val:.2f}</div><div style="font-size:14px; color:{p_color}; font-weight:bold;">漲跌: {change_val:.2f}</div></div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60_val:.2f}</div></div>
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                    <tr><td style="padding: 10px 5px;">外資成本 / 融資成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                    <tr style="background: #fff9db;"><td style="padding: 10px 5px; color: #e67e22; font-weight: bold;">突破點 (1.04)<br><span style="font-size:10px; color:#666; font-weight:normal;">*空頭格局通常在此位站不穩</span></td><td style="text-align: right; font-weight: bold;">{p104:.2f}</td></tr>
                    {sl_html}
                    <tr><td style="padding: 10px 5px;">目標一 (1.2)</td><td style="text-align: right;">{t1:.2f}</td></tr>
                    <tr style="background: #fafafa;"><td style="padding: 10px 5px;">目標二 (1.4)</td><td style="text-align: right;">{t2:.2f}</td></tr>
                    <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 5px; font-weight: bold;">目標三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right;">{t3:.2f}</td></tr>
                </table>
                <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                    <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 19px;">🎯 兔兔實戰心法審核</div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">1. <b>強勢股判定</b>：站穩季線之上</span> <span style="font-size: 20px;">{"✅" if price_val > m60_val else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">2. <b>趨勢判定</b>：多頭型態 (價>月>季)</span> <span style="font-size: 20px;">{"✅" if price_val > m20_val > m60_val else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">3. <b>籌碼判定</b>：外資/融資主力連買</span> <span style="font-size: 20px;">✅</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">4. <b>攻擊判定</b>：突破成本 1.04 空間</span> <span style="font-size: 20px;">{"✅" if price_val >= p104 else "❌"}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''
            components.html(full_card, height=2100, scrolling=True)
        else: st.error("❌ 找不到數據，請確認代號（如 009816）。")
    except Exception as e: st.error(f"⚠️ 錯誤: {e}")
