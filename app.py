import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定 (確保無亂碼，設定網頁分頁小圖示)
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 2. 介面美化 CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; border: none;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.3);
    }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 3. 輸入區
c1, c2 = st.columns(2)
sid = c1.text_input("股票代號", value="4807")
cost_str = c2.text_input("外資/法人成本", value="38.53")

def get_full_data(sid):
    name, df = sid, pd.DataFrame()
    # A. 抓取名稱
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass

    # B. 抓取歷史數據 (yfinance)
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60: break
        except: continue
    
    # C. 備援：如果現價抓不到，改用 twstock 抓即時價 (解決 nan 問題)
    price_val = None
    if not df.empty:
        price_val = float(df['Close'].iloc[-1])
    
    if price_val is None or pd.isna(price_val):
        try:
            rt = twstock.realtime.get(sid)
            if rt and rt['success']:
                price_val = float(rt['realtime']['latest_trade_price'])
        except: pass
        
    return name, df, price_val

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在搬運大數據並繪製 K 線...'):
            name, df, price = get_full_data(sid)

            if price and not pd.isna(price):
                # --- 📈 1. 繪製 K 線圖 ---
                if not df.empty:
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name="K線", increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    # 計算均線
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20 = df['MA20'].iloc[-1]
                    ma60 = df['MA60'].iloc[-1]
                    
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線(60MA)", line=dict(color='#228be6', width=2)))
                    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(l=5, r=5, t=10, b=10), template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    ma60 = 0 # 備援

                # --- 🐰 2. 數據計算與分析 ---
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_god_beast = cost >= (price * 1.7)
                
                # 多頭線型判斷
                is_bull = False
                if not df.empty and not pd.isna(ma20) and not pd.isna(ma60):
                    is_bull = price > ma20 and ma20 > ma60
                
                bull_html = '''
                <div style="background: linear-gradient(135deg, #FFF9C4, #FBC02D); color: #5D4037; padding: 12px; margin: 10px 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #FBC02D; box-shadow: 0 4px 10px rgba(251, 192, 45, 0.2);">
                    🔥 偵測到「多頭線型」排列<br><span style="font-size:12px;">趨勢強勁，適合順勢操作</span>
                </div>
                ''' if is_bull else ""

                if price < cost: strategy, color = "📍 現價低於成本，法人收貨中，適合分批低接。", "#51cf66"
                elif price < p104: strategy, color = f"📍 處於起跑區，站穩 1.04 突破點 ({p104}) 後即起飛。", "#fcc419"
                elif price < t1: strategy, color = "📍 已突破 1.04！目標關卡一 (1.2)，注意短線盤整。", "#ff922b"
                else: strategy, color = f"📍 強勢波段行進中，注意 {t2} 關卡壓力。", "#ff6b6b"

                # --- 🐰 3. 渲染美化卡片 ---
                god_beast_html = f'''<div style="background: #fff9db; color: #856404; padding: 15px; margin: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid #ffeeba;">⚠️ 偵測到「上古神獸」<br>成本過高，建議改用【融資成本】。</div>''' if is_god_beast else ""

                full_card = f'''
                <div style="font-family: sans-serif; background: #fffafb; padding: 5px;">
                    <div style="background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ffe3e3;">
                        <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold;">{name} ({sid})</div>
                        </div>
                        {bull_html}
                        {god_beast_html}
                        <div style="padding: 25px; text-align: center;">
                            <div style="display: flex; justify-content: space-around; align-items: center;">
                                <div><div style="font-size: 12px; color: #888;">當前現價</div><div style="font-size: 42px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                                <div style="border-left: 1px solid #eee; height: 50px;"></div>
                                <div><div style="font-size: 12px; color: #888;">季線 (60MA)</div><div style="font-size: 30px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                            </div>
                        </div>
                        <div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 20px 15px 20px; border-radius: 8px;">
                            <div style="font-weight: bold; color: #ff6b6b; margin-bottom: 5px; font-size: 15px;">🐰 兔兔戰術建議：</div>
                            <div style="font-size: 14px; line-height: 1.5;">{strategy}</div>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 15px; color: #555;">
                            <tr style="background: #fafafa; border-top: 1px solid #eee;"><td style="padding: 12px 20px;">法人原始成本</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                            <tr style="background: #fff9db;"><td style="padding: 12px 20px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                            <tr><td style="padding: 12px 20px;">關卡一 (1.2高點)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                            <tr style="background: #fafafa;"><td style="padding: 12px 20px;">關卡二 (1.4高點)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        </table>
                        <div style="background: #ebfbee; padding: 20px; border-top: 2px dashed #b2f2bb;">
                            <div style="text-align: center; color: #2b8a3e; font-weight: bold; margin-bottom: 12px;">🐰 兔子理財：選股四原則</div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                <div style="font-size: 11px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🚀 <b>優先強勢股</b></div>
                                <div style="font-size: 11px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🤝 <b>法人加碼</b></div>
                                <div style="font-size: 11px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">📉 <b>多頭線型</b></div>
                                <div style="font-size: 11px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🎯 <b>貼近成本</b></div>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card, height=750, scrolling=True)
            else:
                st.error("❌ 無法抓取數據。請檢查代號或稍後再試。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
