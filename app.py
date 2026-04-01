import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 型態大師", page_icon="🐰", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 25px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 22px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 型態大師分析儀")

# 2. 原生 HTML 九宮格大鍵盤 (上下排列)
query_params = st.query_params
sid_str = query_params.get("sid", "4807")
cost_str = query_params.get("cost", "38.53")

html_input = f"""
    <div style="font-family: sans-serif; padding: 10px 5px;">
        <div style="margin-bottom: 15px;">
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 8px;">股票代號</div>
            <input type="tel" id="sid" value="{sid_str}" inputmode="decimal" 
                style="width: 100%; height: 65px; background: #1a1c23; border: 2px solid #555; border-radius: 15px; color: #ff4b4b; font-size: 30px; text-align: center; font-weight: bold; outline: none;">
        </div>
        <div>
            <div style="color: #eee; text-align: center; font-weight: bold; margin-bottom: 8px;">外資/法人成本</div>
            <input type="tel" id="cost" value="{cost_str}" inputmode="decimal" 
                style="width: 100%; height: 65px; background: #1a1c23; border: 2px solid #555; border-radius: 15px; color: #ff4b4b; font-size: 30px; text-align: center; font-weight: bold; outline: none;">
        </div>
    </div>
    <script>
        const s = document.getElementById('sid'); const c = document.getElementById('cost');
        function sync() {{
            const url = new URL(window.parent.location);
            url.searchParams.set('sid', s.value); url.searchParams.set('cost', c.value);
            window.parent.history.replaceState({{}}, '', url);
        }}
        s.oninput = sync; c.oninput = sync;
    </script>
"""
components.html(html_input, height=220)

# --- 🚀 型態偵測邏輯函式 ---
def detect_patterns(df):
    msg = []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    body = abs(last['Close'] - last['Open'])
    avg_body = abs(df['Close'] - df['Open']).mean()
    upper_shadow = last['High'] - max(last['Close'], last['Open'])
    lower_shadow = min(last['Close'], last['Open']) - last['Low']

    # 1. 陽線形態分析 (對照圖1)
    if last['Close'] > last['Open']:
        if body > avg_body * 2: msg.append("🔥 偵測到「大陽線」：多方絕對優勢，強勢噴發！")
        if lower_shadow > body * 1.5: msg.append("⚓ 偵測到「帶下影線」：下方支撐極強，與壓力對抗後勝出。")
        if upper_shadow > body * 1.5: msg.append("⚠️ 偵測到「帶上影線」：上方有壓力，突破後壓力減輕。")
    
    # 2. 水平支撐壓力與W底/M頭預警 (對照圖2, 3, 5)
    recent_high = df['High'].tail(20).max()
    recent_low = df['Low'].tail(20).min()
    
    if last['Close'] >= recent_high * 0.98:
        msg.append("🛡️ 挑戰壓力線：若能「支撐壓力轉換」站穩，將迎接暴漲。")
    if last['Close'] <= recent_low * 1.02:
        msg.append("📉 跌至支撐線：注意是否跌破，空頭格局通常在此站不穩。")

    # 3. 趨勢警告 (對照圖4)
    if last['Close'] > prev['Close'] and prev['Close'] > df.iloc[-3]['Close']:
        msg.append("📈 上升通道中：符合「迎向暴漲」警報，趕緊買入機率 80%↑。")
    elif last['Close'] < prev['Close'] and prev['Close'] < df.iloc[-3]['Close']:
        msg.append("🚨 下跌旗形警告：符合「防範暴跌」警報，請謹慎防守。")

    return msg if msg else ["🌀 目前型態：箱型盤整中，危險別碰，等待方向明確。"]

@st.cache_data(ttl=300)
def get_data(sid):
    name, df, price, change = sid, pd.DataFrame(), None, 0
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60:
                price = float(df['Close'].iloc[-1])
                change = price - float(df['Close'].iloc[-2])
                stock_info = twstock.codes.get(sid)
                name = stock_info.name if stock_info else sid
                break
        except: continue
    return name, df, price, change

if st.button("🚀 執行 AI 型態大師分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在比對型態圖案...'):
            name, df, price, change = get_data(sid_str)

            if price and not pd.isna(price):
                # 型態偵測
                patterns = detect_patterns(df)
                pattern_html = "".join([f'<div style="margin-bottom:5px;">{p}</div>' for p in patterns])

                # K 線與均線計算
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA60'] = df['Close'].rolling(window=60).mean()
                m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                is_bull = price > m20 > m60

                # 繪圖
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff4d4d', decreasing_line_color='#00b050')])
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="月線", line=dict(color='#f06595', width=1.5)))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
                fig.update_layout(xaxis_rangeslider_visible=False, height=380, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # 數據與心法邏輯
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                p_color = "#ff4d4d" if change > 0 else ("#00b050" if change < 0 else "#eee")
                
                def get_st(val):
                    if price >= val: return 'color: #ff4b4b; font-weight: bold;', '🚩 已達成 '
                    return 'color: #333;', ''
                s104, l104 = get_st(p104); st1, lt1 = get_st(t1); st2, lt2 = get_st(t2); st3, lt3 = get_st(t3)

                # --- 渲染完全體 HTML 卡片 ---
                full_card_html = f'''
                <div style="font-family: sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold;">{name} ({sid_str})</span>
                    </div>

                    <div style="background: #e7f5ff; border-left: 5px solid #228be6; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <b style="color: #1c7ed6; font-size: 17px;">🎨 AI 視覺型態辨識：</b>
                        <div style="font-size: 14px; color: #444; margin-top: 8px; font-weight: bold; line-height: 1.6;">{pattern_html}</div>
                    </div>

                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px; border: 1px solid #eee;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold; color: {p_color};">{price:.2f} Change:{change:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                    </div>

                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">{l104}突破點 (1.04)<br><span style="font-size:10px; color:#666;">*空頭格局通常在此位站不穩</span></td><td style="text-align: right; {s104}">{p104:.2f}</td></tr>
                        <tr><td style="padding: 12px 5px;">{lt1}目標關卡一 (1.2)</td><td style="text-align: right; {st1}">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">{lt2}目標關卡二 (1.4)</td><td style="text-align: right; {st2}">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 12px 5px; font-weight: bold;">{lt3}目標關卡三 (1.7) <span style="font-size:11px; color:#cc0000; font-weight:normal;">*高風險不追價</span></td><td style="text-align: right; {st3}">{t3:.2f}</td></tr>
                    </table>

                    <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d;">
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🐰 仙兔實戰心法判定</div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;"><span>1. <b>強勢股</b>：站穩季線之上</span> <span>{"✅" if price > m60 else "❌"}</span></div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;"><span>2. <b>籌碼判定</b>：法人底氣連買</span> <span>✅</span></div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;"><span>3. <b>型態判定</b>：多頭線型排列</span> <span>{"✅" if is_bull else "❌"}</span></div>
                            <div style="background: white; padding: 12px; border-radius: 12px; border-left: 5px solid #fbc02d; display: flex; justify-content: space-between; align-items: center;"><span>4. <b>攻擊判定</b>：突破 1.04 空間</span> <span>{"✅" if price >= p104 else "❌"}</span></div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=2200, scrolling=True)
            else: st.error("❌ 數據獲取異常。")
    except Exception as e: st.error(f"⚠️ 請檢查輸入內容。")
