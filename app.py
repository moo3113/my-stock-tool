import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 22px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 2. 原生 HTML 數字輸入框 (上下排列，喚起九宮格大鍵盤)
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
components.html(html_input_component, height=240)

@st.cache_data(ttl=300)
def get_data(sid):
    name, df, price, change = sid, pd.DataFrame(), None, 0
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 2:
                price = float(df['Close'].iloc[-1])
                change = price - float(df['Close'].iloc[-2])
                break
        except: continue
    return name, df, price, change

if st.button("🚀 執行 AI 數據大集合分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在審核選股條件與線型...'):
            name, df, price, change = get_data(sid_str)

            if price and not pd.isna(price):
                # --- 1. 線型判定 ---
                trend_html, m20, m60, is_bull = "", 0, 0, False
                is_bear = False # 判定是否為空頭
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    is_bull = price > m20 > m60
                    is_bear = price < m20 < m60
                    
                    if is_bull: t_lab, t_grd, t_c = "🔥 多頭排列 (強勢漲勢)", "linear-gradient(135deg, #fff9db, #fcc419)", "#5d4037"
                    elif is_bear: t_lab, t_grd, t_c = "❄️ 空頭排列 (保守觀望)", "linear-gradient(135deg, #e9ecef, #adb5bd)", "#343a40"
                    else: t_lab, t_grd, t_c = "🌀 橫盤整盤 (等待突破)", "linear-gradient(135deg, #e3fafc, #99e9f2)", "#0b7285"
                    trend_html = f'<div style="background: {t_grd}; color: {t_c}; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold;">{t_lab}</div>'

                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
                    fig.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # --- 2. 數據精算 ---
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                p_color = "#ff4d4d" if change > 0 else ("#00b050" if change < 0 else "#333")
                
                def get_st(val):
                    if price >= val: return 'color: #ff4b4b; font-weight: bold;', '🚩 已達成 '
                    return 'color: #333;', ''

                s104, l104 = get_st(p104)
                st1, lt1 = get_st(t1)
                st2, lt2 = get_st(t2)
                st3, lt3 = get_st(t3)

                stop_loss = round(p104 * 0.94, 2)
                sl_row = f'''<tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 12px 5px; color: #cc0000; font-weight: bold;">風控回檔位 (-6%)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{stop_loss:.2f}</td></tr>''' if price >= p104 else ""

                # --- 3. 心法判定 ---
                check_1 = "✅" if price > m60 else "❌"
                check_2 = "✅" 
                check_3 = "✅" if is_bull else "❌"
                check_4 = "✅" if price >= p104 else "❌"

                full_card_html = f'''
                <div style="font-family: -apple-system, sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold; color: white;">{name} ({sid_str})</span>
                    </div>
                    {trend_html}
                    
                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold; color: {p_color};">{price:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                    </div>

                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">{l104}突破點 (1.04)<br><span style="font-size:10px; font-weight:normal; color:#666;">*空頭格局通常在此位站不穩</span></td><td style="text-align: right; {s104}">{p104:.2f}</td></tr>
                        {sl_row}
                        <tr><td style="padding: 12px 5px;">{lt1}目標關卡一 (1.2)</td><td style="text-align: right; {st1}">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">{lt2}目標關卡二 (1.4)</td><td style="text-align: right; {st2}">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 12px 5px; font-weight: bold;">{lt3}目標關卡三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right; {st3}">{t3:.2f}</td></tr>
                    </table>

                    <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🐰 仙兔實戰心法判定</div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><b style="font-size: 16px;">1. 趨勢判定：強勢股</b> <span style="font-size: 22px;">{check_1}</span></div>
                                <div style="font-size: 13px; color: #666;">股價必須站穩季線之上。季線是生命線，站不穩就代表尚未轉強。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><b style="font-size: 16px;">2. 籌碼判定：法人底氣</b> <span style="font-size: 22px;">{check_2}</span></div>
                                <div style="font-size: 13px; color: #666;">觀察法人於低位盤整區是否連續買進。有籌碼墊底，突破才有力。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><b style="font-size: 16px;">3. 型態判定：多頭線型</b> <span style="font-size: 22px;">{check_3}</span></div>
                                <div style="font-size: 13px; color: #666;">月線 > 季線且股價向上。代表短中長期趨勢同步，上升慣性強。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><b style="font-size: 16px;">4. 攻擊判定：突破空間</b> <span style="font-size: 22px;">{check_4}</span></div>
                                <div style="font-size: 13px; color: #666;">現價超過 1.04 突破點代表脫離收貨區，正式進入主升波。</div>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=2100, scrolling=True)
            else: st.error("❌ 數據獲取異常。")
    except Exception as e: st.error(f"⚠️ 請檢查輸入內容。")
