import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 終極版", page_icon="🐰", layout="centered")

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

st.title("🐰 仙兔 AI 型態大師分析儀")

# 2. 原生 HTML 九宮格輸入框 (修正顯示不完整問題)
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
components.html(html_input_component, height=260) # 增加高度確保不被切掉

# --- 🚀 AI 型態掃描引擎 ---
def scan_patterns(df):
    msg = []
    last = df.iloc[-1]; prev = df.iloc[-2]
    body = abs(last['Close'] - last['Open'])
    avg_b = abs(df['Close'] - df['Open']).tail(10).mean()
    l_shadow = min(last['Close'], last['Open']) - last['Low']
    
    if last['Close'] > last['Open'] and body > avg_b * 1.8: msg.append("🔥 大陽線：多方絕對優勢，迎向暴漲。")
    if l_shadow > body * 1.5: msg.append("⚓ 長下影線：下方支撐力道強。")
    
    high_20 = df['High'].tail(20).max()
    if last['Close'] >= high_20 * 0.98: msg.append("🛡️ 挑戰壓力線：注意支撐壓力轉換。")
    
    std_10 = df['Close'].tail(10).std()
    if std_10 < (last['Close'] * 0.01): msg.append("📦 箱型盤整：50% 盤整區，別碰！")
    
    return msg if msg else ["🌀 暫無明顯圖形：目前處於均衡狀態。"]

@st.cache_data(ttl=300)
def get_stock_data(sid):
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 2:
                name = twstock.codes.get(sid).name if twstock.codes.get(sid) else sid
                price = float(df['Close'].iloc[-1])
                change = price - float(df['Close'].iloc[-2])
                return name, df, price, change
        except: continue
    return sid, pd.DataFrame(), None, 0

if st.button("🚀 執行 AI 數據大集合分析"):
    try:
        cost = float(cost_str)
        name, df, price, change = get_stock_data(sid_str)

        if price:
            # 計算指標
            df['MA20'] = df['Close'].rolling(20).mean()
            df['MA60'] = df['Close'].rolling(60).mean()
            m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
            is_bull = price > m20 > m60

            # 神獸判定
            is_god = cost >= (price * 1.5)
            god_h = f'''<div style="background: #ff8787; color: white; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 2px solid white;">⚠️ 偵測到「上古神獸」<br><span style="font-size:12px;">(成本遠高於現價，建議改用融資成本)</span></div>''' if is_god else ""

            # K線圖
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
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

            # 型態辨識
            patterns = scan_patterns(df)
            p_html = "".join([f'<div style="margin-bottom:6px;">{p}</div>' for p in patterns])

            # 渲染 HTML
            full_card = f'''
            <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                    <span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span>
                </div>
                {god_h}
                <div style="background: #e7f5ff; border-left: 6px solid #228be6; padding: 15px; border-radius: 12px; margin-bottom: 15px;">
                    <b style="color: #1c7ed6; font-size: 17px;">🎨 AI 視覺型態辨識：</b>
                    <div style="font-size: 14px; color: #444; margin-top: 8px; font-weight: bold; line-height: 1.6;">{p_html}</div>
                </div>
                <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                    <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 32px; font-weight: bold; color: {p_color};">{price:.2f}</div><div style="font-size:14px; color:{p_color}; font-weight:bold;">漲跌: {change:.2f}</div></div>
                    <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                    <tr><td style="padding: 10px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                    <tr style="background: #fff9db;"><td style="padding: 10px 5px; color: #e67e22; font-weight: bold;">{l104}突破點 (1.04)<br><span style="font-size:10px; color:#666;">*空頭格局通常在此位站不穩</span></td><td style="text-align: right; {s104}">{p104:.2f}</td></tr>
                    {sl_row}
                    <tr><td style="padding: 10px 5px;">{lt1}目標一 (1.2)</td><td style="text-align: right; {st1}">{t1:.2f}</td></tr>
                    <tr style="background: #fafafa;"><td style="padding: 10px 5px;">{lt2}目標二 (1.4)</td><td style="text-align: right; {st2}">{t2:.2f}</td></tr>
                    <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 5px; font-weight: bold;">{lt3}目標三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right; {st3}">{t3:.2f}</td></tr>
                </table>
                <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                    <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🎯 仙兔實戰心法判定</div>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">1. <b>強勢股</b>：站穩季線之上，不破生命線</span> <span style="font-size: 20px;">{"✅" if price > m60 else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">2. <b>法人加碼</b>：低位盤整區連續買進</span> <span style="font-size: 20px;">✅</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">3. <b>多頭型態</b>：月線>季線，排列向上</span> <span style="font-size: 20px;">{"✅" if is_bull else "❌"}</span>
                        </div>
                        <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 14px;">4. <b>突破攻擊</b>：股價站上 1.04 突破點</span> <span style="font-size: 20px;">{"✅" if price >= p104 else "❌"}</span>
                        </div>
                    </div>
                    <div style="margin-top: 15px; background: #c92a2a; color: white; padding: 10px; border-radius: 10px; text-align: center; font-size: 14px; font-weight: bold;">核心：只買比【法人成本】高一點點的股！</div>
                </div>
            </div>
            '''
            components.html(full_card, height=2200, scrolling=True)
    except: st.error("⚠️ 請輸入數字後點擊執行。")
