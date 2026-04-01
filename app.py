import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 🌟 終極金兔設定 (更換全新圖址避開系統快取)
# ==========================================
# 換了一個來自不同網域的金色兔子，強制系統重新抓取
GOLD_RABBIT_ICON = "https://img.icons8.com/color/512/rabbit.png" 
APP_TITLE = "仙兔 AI 分析儀"

# 1. 網頁基礎設定
st.set_page_config(page_title=APP_TITLE, page_icon=GOLD_RABBIT_ICON, layout="centered")

# 2. 暴力破解系統快取 (加入 PWA 描述標籤)
st.markdown(f"""
    <head>
        <link rel="icon" type="image/png" href="{GOLD_RABBIT_ICON}?v=99">
        <link rel="apple-touch-icon" sizes="180x180" href="{GOLD_RABBIT_ICON}?v=99">
        <link rel="apple-touch-icon-precomposed" href="{GOLD_RABBIT_ICON}?v=99">
        
        <meta name="apple-mobile-web-app-title" content="{APP_TITLE}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        
        <meta property="og:image" content="{GOLD_RABBIT_ICON}?v=99">
        <meta name="twitter:image" content="{GOLD_RABBIT_ICON}?v=99">
    </head>
    """, unsafe_allow_html=True)

# 3. 介面美化 CSS
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
    </style>
    """, unsafe_allow_html=True)

st.title(f"🐰 {APP_TITLE}")

# --- 以下保留核心功能邏輯 (與先前版本一致) ---
c1, c2 = st.columns(2)
sid = c1.text_input("股票代號", value="1815")
cost_str = c2.text_input("外資/法人成本", value="105.6")

def get_data(sid):
    name, price, ma60 = sid, None, None
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="100d")
            if not df.empty:
                price = df['Close'].iloc[-1]
                ma60 = df['Close'].rolling(window=60).mean().iloc[-1]
                break
        except: continue
    return name, price, ma60

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('正在載入金兔大數據...'):
            name, price, ma60 = get_data(sid)
            if price and ma60:
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_god_beast = cost >= (price * 1.7)
                if price < cost: strategy, color = "📍 現價低於成本，法人收貨中，適合分批低接。", "#51cf66"
                elif price < p104: strategy, color = f"📍 處於起跑區，站穩 1.04 突破點 ({p104}) 後即起飛。", "#fcc419"
                elif price < t1: strategy, color = "📍 已突破 1.04！目標關卡一，注意短線盤整。", "#ff922b"
                else: strategy, color = f"📍 強勢波段行進中，注意 {t2} 關卡壓力。", "#ff6b6b"
                god_beast_html = f'<div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #5d4037; padding: 15px; margin: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid #FF8C00;">✨ 偵測到「上古神獸」✨<br>成本過高，建議改用【融資成本】。</div>' if is_god_beast else ""
                ai_trend = "📈 趨勢偏多，股價在季線之上。" if price > ma60 else "📉 趨勢偏弱，股價在季線之下。"
                bias = ((price - ma60) / ma60) * 100
                ai_bias = f"<br>🚨 正乖離率過大 ({bias:.1f}%)，隨時有修正風險。" if bias > 15 else ""
                full_card = f'''<div style="font-family: -apple-system, sans-serif; background: #fffafb; padding: 5px;"><div style="background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ffe3e3;"><div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center;"><div style="font-size: 24px; font-weight: bold;">{name} ({sid})</div></div>{god_beast_html}<div style="padding: 25px; text-align: center;"><div style="display: flex; justify-content: space-around; align-items: center;"><div><div style="font-size: 12px; color: #888;">當前現價</div><div style="font-size: 42px; font-weight: bold; color: {color};">{price:.2f}</div></div><div style="border-left: 1px solid #eee; height: 50px;"></div><div><div style="font-size: 12px; color: #888;">季線 (60MA)</div><div style="font-size: 30px; font-weight: bold; color: #444;">{ma60:.2f}</div></div></div></div><div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 20px 15px 20px; border-radius: 8px;"><div style="font-weight: bold; color: #ff6b6b; margin-bottom: 5px;">🐰 兔兔戰術建議：</div><div style="font-size: 14px;">{strategy}</div></div><div style="background: #f0f7ff; border-left: 5px solid #228be6; padding: 15px; margin: 0 20px 20px 20px; border-radius: 8px;"><div style="font-weight: bold; color: #228be6; margin-bottom: 5px;">🤖 AI 智慧分析：</div><div style="font-size: 14px;">{ai_trend}{ai_bias}</div></div><table style="width: 100%; border-collapse: collapse; font-size: 15px; color: #555;"><tr style="background: #fafafa; border-top: 1px solid #eee;"><td style="padding: 12px 20px;">法人原始成本</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{cost:.2f}</td></tr><tr style="background: #fff9db;"><td style="padding: 12px 20px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr><tr><td style="padding: 12px 20px;">關卡一 (1.2)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t1:.2f}</td></tr><tr style="background: #fafafa;"><td style="padding: 12px 20px;">關卡二 (1.4)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t2:.2f}</td></tr><tr style="border-bottom: 1px solid #eee;"><td style="padding: 12px 20px;">關卡三 (1.7)</td><td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t3:.2f}</td></tr></table><div style="background: #ebfbee; padding: 20px; border-top: 2px dashed #b2f2bb;"><div style="text-align: center; color: #2b8a3e; font-weight: bold; margin-bottom: 12px;">🐰 兔子理財：選股四原則</div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;"><div style="font-size: 12px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🚀 <b>優先強勢股</b></div><div style="font-size: 12px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🤝 <b>法人持續加碼</b></div><div style="font-size: 12px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">📉 <b>確認多頭線型</b></div><div style="font-size: 12px; color: #2b8a3e; background: white; padding: 8px; border-radius: 8px; border: 1px solid #d3f9d8;">🎯 <b>現價離成本近</b></div></div></div></div></div>'''
                components.html(full_card, height=880, scrolling=True)
            else:
                st.error("❌ 無法獲取數據。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
