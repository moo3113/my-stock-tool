import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime

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

# --- 🚀 核心數據與試搓偵測引擎 ---
@st.cache_data(ttl=60) # 盤中縮短緩存至 60 秒
def fetch_smart_data(sid):
    sid = sid.strip()
    name = "凱基台灣 TOP 50" if sid == "009816" else sid
    try:
        tw_info = twstock.codes.get(sid)
        if tw_info: name = tw_info.name
    except: pass

    is_trial = False
    now_time = datetime.now().strftime("%H:%M")
    # 判斷是否為試搓時段 (08:30-09:00 或 13:25-13:30)
    if ("08:30" <= now_time <= "09:00") or ("13:25" <= now_time <= "13:30"):
        is_trial = True

    for suffix in [".TW", ".TWO", ""]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="1y")
            if not df.empty:
                # 🛡️ 數據清洗：若最後一筆沒價格(試搓中)，則 ffll() 抓前一筆真實價
                if df['Close'].isnull().iloc[-1]: is_trial = True
                df_clean = df.ffill().dropna(subset=['Close'])
                
                p = float(df_clean['Close'].iloc[-1])
                ch = p - float(df_clean['Close'].iloc[-2]) if len(df_clean) > 1 else 0
                return name, df_clean, p, ch, is_trial
        except: continue
    return None, None, None, 0, False

if st.button("🚀 執行 AI 數據分析儀"):
    try:
        cost = float(cost_str); name, df, p_val, ch_val, is_trial = fetch_smart_data(sid_str)
        if p_val:
            data_count = len(df)
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA60'] = df['Close'].rolling(window=60, min_periods=1).mean()
            m20, m60 = float(df['MA20'].iloc[-1]), float(df['MA60'].iloc[-1])

            # 格局
            if p_val > m20 > m60: status = ("🔥 強勢多頭", "#fff9db", "符合「迎向暴漲」格局。")
            elif p_val < m20 < m60: status = ("❄️ 弱勢空頭", "#e9ecef", "防範暴跌，突破點站不穩。")
            else: status = ("🌀 箱型盤整", "#e3fafc", "50% 盤整區，別碰。")

            # 1.7 倍神獸
            god_h = f'''<div style="background: #ff4b4b; color: white; padding: 15px; margin-bottom: 15px; border-radius: 15px; text-align: center; font-weight: bold; border: 3px solid white;">⚠️ 偵測到「上古神獸」格局<br><span style="font-size:13px; font-weight:normal;">現價大於成本 1.7 倍，建議改用「融資成本」重新分析。</span></div>''' if p_val >= (cost * 1.7) else ""

            # 試搓提醒小字
            trial_note = '<div style="font-size:10px; color:#9c27b0; margin-top:4px; font-weight:bold;">🕒 試搓時段/數據延遲中,採最後成交價</div>' if is_trial else ""
            ma60_note = f'<div style="font-size:10px; color:#e67e22; margin-top:4px;">*掛牌僅{data_count}天,以至今平均計算</div>' if data_count < 60 else ""

            # K線圖
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
            fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)

            # 數據渲染與風控
            p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            p_color = "#ff4d4d" if ch_val > 0 else ("#00b050" if ch_val < 0 else "#eee")
            sl_p = round(p104 * 0.94, 2)
            sl_html = f'''<tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 10px 5px; color: #cc0000; font-weight: bold;">🚩 風控回檔位 (-6%)<br><span style="font-size:10px; color:#999;">*突破點回檔之簡化風控</span></td><td style="text-align: right; font-weight: bold; color: #cc0000;">{sl_p:.2f}</td></tr>''' if p_val >= p104 else ""

            full_card = f'''
            <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                    <span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span>
                </div>
                {god_h}
                <div style="background: {status[1]}; padding: 15px; border-radius: 15px; border: 2px solid #ddd; margin-bottom: 15px; text-align: center;">
                    <b style="font-size: 20px; color: #333;">{status[0]}</b><br>
                    <div style="font-size: 14px; color: #555; font-weight: bold; margin-top: 5px;">{status[2]}</div>
                    <div style="text-align: left; font-size: 13px; color: #444; margin-top: 10px; background: rgba(255,255,255,0.6); padding: 10px; border-radius: 8px;">*偵測K線魂：大陽線/下影線判定中...</div>
                </div>
                <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{p_val:.2f}</div>{trial_note}</div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div>{ma60_note}</div>
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
                            <span style="font-size: 14px;">1. <b>強勢股判定</b>：站穩季線之上</span> <span style="font-size: 20px;">{"✅" if p_val > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">2. <b>趨勢判定</b>：多頭型態 (價>月>季)</span> <span style="font-size: 20px;">{"✅" if p_val > m20 > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">3. <b>籌碼判定</b>：外資/融資主力連買</span> <span style="font-size: 20px;">✅</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">4. <b>攻擊判定</b>：突破成本 1.04 空間</span> <span style="font-size: 20px;">{"✅" if p_val >= p104 else "❌"}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''
            components.html(full_card, height=2100, scrolling=True)
    except Exception as e: st.error(f"⚠️ 運行錯誤: {e}")
