import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# CSS：深色背景 + 紅色亮眼輸入框 + 標題文字美化
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* 強化輸入框：紅色文字、加大字體、隱藏加減鈕 */
    .stNumberInput div[data-baseweb="input"] {
        background-color: #1a1c23 !important;
        border-radius: 15px !important;
        border: 2px solid #555 !important;
        min-height: 70px !important;
    }
    .stNumberInput input {
        color: #ff4b4b !important; 
        font-size: 28px !important; 
        text-align: center !important;
        font-weight: bold !important;
    }
    button[title="Step up"], button[title="Step down"] { display: none !important; }

    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 20px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        margin-top: 10px;
    }
    label { color: #eee !important; font-weight: bold !important; font-size: 17px !important; margin-bottom: 15px !important; display: block; text-align: center; }
    </style>
    
    <script>
    // 終極強制數字鍵盤腳本 (iOS/Android 通用)
    var forceNumeric = function() {
        var inputs = window.parent.document.querySelectorAll('input[type="number"]');
        inputs.forEach(function(input) {
            input.setAttribute('inputmode', 'decimal'); 
            input.setAttribute('pattern', '[0-9.]*');
            input.setAttribute('step', 'any');
        });
    };
    setTimeout(forceNumeric, 1000);
    setInterval(forceNumeric, 2000);
    </script>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 2. 輸入區
c1, c2 = st.columns(2)
with c1: sid_num = st.number_input("股票代號", value=4807, step=1, format="%d")
with c2: cost = st.number_input("外資/法人成本", value=38.53, step=0.01, format="%.2f")

@st.cache_data(ttl=300)
def get_data(sid_str):
    name, df, price = sid_str, pd.DataFrame(), None
    try:
        stock_info = twstock.codes.get(sid_str)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid_str}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60:
                price = float(df['Close'].iloc[-1])
                break
        except: continue
    return name, df, price

if st.button("🚀 執行 AI 數據大集合分析"):
    try:
        sid_str = str(int(sid_num))
        with st.spinner('金兔正在搬運大集合數據...'):
            name, df, price = get_data(sid_str)

            if price and not pd.isna(price):
                # --- 📈 1. K 線圖與線型判定 ---
                trend_html = ""
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    m20, m60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    
                    if price > m20 > m60:
                        t_label, t_grad, t_c = "🔥 偵測到「多頭線型」排列", "linear-gradient(135deg, #fff9db, #fcc419)", "#5d4037"
                    elif price < m20 < m60:
                        t_label, t_grad, t_c = "❄️ 偵測到「空頭線型」排列", "linear-gradient(135deg, #e9ecef, #adb5bd)", "#343a40"
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
                else: m20, m60 = 0, 0

                # --- 2. 數據精算 ---
                p104 = round(cost*1.04, 2)
                t1, t2, t3 = round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                stop_loss = round(p104 * 0.94, 2) 
                
                # AI 戰術建議 (黑色 15px)
                if price < cost: strategy = f"📍 低推上收貨中。現價離法人成本還有 {round(cost-price, 2)} 元，站穩成本線即轉強。"
                elif price < p104: strategy = f"📍 蓄勢待發！離 1.04 起飛點 ({p104}) 僅差 {round(p104-price, 2)} 元，站穩即正式起飛。"
                elif price < t1: 
                    over_pct = round(((price / p104) - 1) * 100, 1)
                    strategy = f"✅ 已成功突破 1.04 位階 (超越 {over_pct}%)！目標直指 1.2 關卡 ({t1})，留意風控位 {stop_loss}。"
                else: strategy = f"🔥 強勢波段衝刺中！已站上 1.2 目標。接近 1.4 ({t2}) 或 1.7 ({t3}) 請務必嚴格止盈。"

                # --- 3. 完整 HTML 卡片 ---
                full_card_html = f'''
                <div style="font-family: -apple-system, sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold; color: white;">{name} ({sid_str})</span>
                    </div>
                    {trend_html}
                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold;">{price:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{m60:.2f}</div></div>
                    </div>
                    <div style="background: #fff5f5; border-left: 6px solid #ff4b4b; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
                        <div style="font-weight: bold; color: #ff4b4b; font-size: 17px; margin-bottom: 5px;">🐰 AI 戰術建議：</div>
                        <div style="font-size: 15px; font-weight: bold; color: #333; line-height: 1.4;">{strategy}</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 25px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                        <tr style="background: #fff0f0; border: 1.5px dashed #ff8787;"><td style="padding: 12px 5px; color: #cc0000; font-weight: bold;">風控回檔位 (-6%)</td><td style="text-align: right; font-weight: bold; color: #cc0000;">{stop_loss:.2f}</td></tr>
                        <tr><td style="padding: 12px 5px;">目標關卡一 (1.2)</td><td style="text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">目標關卡二 (1.4)</td><td style="text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                        <tr style="border-bottom: 1px solid #eee; color: #cc0000;"><td style="padding: 12px 5px; font-weight: bold;">目標關卡三 (1.7) <span style="font-size:11px; font-weight:normal;">*不建議追價</span></td><td style="text-align: right; font-weight: bold;">{t3:.2f}</td></tr>
                    </table>
                    <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d; margin-top: 10px;">
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🐰 兔子理財小學堂：買股心法</div>
                        <div style="background: #fef9e7; padding: 15px; border-radius: 12px; margin-bottom: 18px; text-align: center; border: 1px dashed #fbc02d;">
                            <div style="color: #c92a2a; font-weight: bold; font-size: 17px;">核心：買比【法人成本】高一點點的股！</div>
                            <div style="color: #5d4037; font-size: 14px; margin-top: 5px; font-weight: bold;">低位盤整 + 股價推升 = 主力收貨完成</div>
                        </div>
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 17px;">🎯 選股四原則實戰說明</div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><div style="font-size: 15px; font-weight: bold; color: #c92a2a;">1. 強勢股</div><div style="font-size: 13px; color: #666;">站穩季線 (60MA) 之上。</div></div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><div style="font-size: 15px; font-weight: bold; color: #c92a2a;">2. 法人加碼</div><div style="font-size: 13px; color: #666;">觀察法人於盤整時是否連續買超。</div></div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><div style="font-size: 15px; font-weight: bold; color: #c92a2a;">3. 多頭線型</div><div style="font-size: 13px; color: #666;">股價 > 月線 > 季線的黃金排列。</div></div>
                            <div style="background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #fbc02d; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><div style="font-size: 15px; font-weight: bold; color: #c92a2a;">4. 成本空間</div><div style="font-size: 13px; color: #666;">理想買點應靠近法人平均成本。</div></div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=2000, scrolling=True)
            else:
                st.error("❌ 抓取數據失敗。")
    except Exception as e:
        st.error(f"⚠️ 請檢查輸入內容。")
