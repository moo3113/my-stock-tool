import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# CSS：美化背景與按鈕
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.8em; 
        background: linear-gradient(135deg, #c92a2a, #ff4b4b); 
        color: white; font-weight: bold; border: none; font-size: 20px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    label { color: #eee !important; font-weight: bold; font-size: 17px; display: block; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析儀")

# 2. 終極解決方案：使用 HTML 直接生成輸入框，強制喚起數字鍵盤
# 我們將輸入值存放在 URL 或使用 Streamlit 的實驗性功能，這裡用最穩定的方式
col1, col2 = st.columns(2)

with col1:
    st.write("股票代號")
    sid = st.text_input(" ", value="4807", label_visibility="collapsed", key="sid")
with col2:
    st.write("外資/法人成本")
    cost_str = st.text_input(" ", value="38.53", label_visibility="collapsed", key="cost")

# 這裡注入一段 JavaScript，在頁面加載時強制把上面的 input 變成數字型
components.html("""
    <script>
    var inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(function(input) {
        input.setAttribute('type', 'decimal'); // 針對部分瀏覽器
        input.setAttribute('inputmode', 'decimal'); // 強制喚起數字鍵盤
        input.setAttribute('style', 'color: #ff4b4b !important; font-size: 28px !important; text-align: center !important; font-weight: bold !important;');
    });
    </script>
    """, height=0)

@st.cache_data(ttl=300)
def get_data(sid):
    name, df, price = sid, pd.DataFrame(), None
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="150d")
            if not df.empty and len(df) >= 60:
                price = float(df['Close'].iloc[-1])
                break
        except: continue
    return name, df, price

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('金兔正在偵測波浪與線型...'):
            name, df, price = get_data(sid)

            if price and not pd.isna(price):
                if not df.empty:
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    ma20, ma60 = df['MA20'].iloc[-1], df['MA60'].iloc[-1]
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#ff4d4d', decreasing_line_color='#00b050'
                    )])
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name="季線", line=dict(color='#4dabf7', width=2)))
                    fig.update_layout(
                        xaxis_rangeslider_visible=True, xaxis_rangeslider_thickness=0.08,
                        height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10,r=10,t=10,b=10), dragmode='pan', hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else: ma20, ma60 = 0, 0

                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_bull = price > ma20 > ma60 if ma60 > 0 else False
                is_god = cost >= (price * 1.5) 
                
                if price < cost:
                    strategy = f"📍 低推上收貨中。現價離法人成本還有 {round(cost-price, 2)} 元，站穩成本線即轉強。"
                    color = "#51cf66"
                elif price < p104:
                    strategy = f"📍 蓄勢待發！離 1.04 起飛點 ({p104}) 僅差 {round(p104-price, 2)} 元，站穩即正式起飛。"
                    color = "#fcc419"
                elif price < t1:
                    over_104_pct = round(((price / p104) - 1) * 100, 1)
                    strategy = f"✅ 已成功突破 1.04 位階 (超越 {over_104_pct}%)！目標直指 1.2 關卡 ({t1})。"
                    color = "#ff922b"
                elif price < t2:
                    over_t1_pct = round(((price / t1) - 1) * 100, 1)
                    strategy = f"🔥 正式站上 1.2 關卡 (超越 {over_t1_pct}%)！波段強勢衝刺，觀察 1.4 壓力點 ({t2})。"
                    color = "#ff4b4b"
                else:
                    strategy = f"🚨 極度高檔警戒！股價已站上 1.4 關卡 ({t2})，潛在 1.7 神獸點為 {t3}，請嚴格止盈。"
                    color = "#ff4b4b"

                bull_html = f'''<div style="background: linear-gradient(135deg, #fff9db, #fcc419); color: #5d4037; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold; border: 1px solid #fbc02d;">🔥 偵測到「多頭線型」排列</div>''' if is_bull else ""
                god_html = f'''<div style="background: #ff8787; color: white; padding: 12px; margin-bottom: 15px; border-radius: 12px; text-align: center; font-weight: bold;">⚠️ 偵測到「上古神獸」<br><span style="font-size:12px;">(建議更改為「融資成本」重新分析)</span></div>''' if is_god else ""

                full_card_html = f'''
                <div style="font-family: -apple-system, sans-serif; background: white; padding: 15px; border-radius: 25px; color: #333;">
                    <div style="background: linear-gradient(135deg, #c92a2a, #ff4b4b); color: white; padding: 18px; text-align: center; border-radius: 20px; margin-bottom: 15px;">
                        <span style="font-size: 24px; font-weight: bold; color: white;">{name} ({sid})</span>
                    </div>
                    {bull_html} {god_html}
                    <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; background: #fdfdfd; padding: 15px; border-radius: 15px;">
                        <div><div style="font-size: 13px; color: #999;">當前現價</div><div style="font-size: 38px; font-weight: bold; color: {color};">{price:.2f}</div></div>
                        <div><div style="font-size: 13px; color: #999;">季線 (60MA)</div><div style="font-size: 32px; font-weight: bold; color: #444;">{ma60:.2f}</div></div>
                    </div>
                    
                    <div style="background: #fff5f5; border-left: 6px solid #ff4b4b; padding: 15px; margin-bottom: 20px; border-radius: 8px;">
                        <div style="font-weight: bold; color: #ff4b4b; font-size: 17px; margin-bottom: 5px;">🐰 AI 戰術建議：</div>
                        <div style="font-size: 14px; font-weight: bold; color: #333; line-height: 1.4;">{strategy}</div>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-bottom: 20px;">
                        <tr style="border-top: 1px solid #eee;"><td style="padding: 12px 5px;">法人平均成本</td><td style="text-align: right; font-weight: bold;">{cost:.2f}</td></tr>
                        <tr style="background: #fff9db;"><td style="padding: 12px 5px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td><td style="text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td style="padding: 12px 5px;">關卡一 (1.2)</td><td style="text-align: right; font-weight: bold;">{t1:.2f}</td></tr>
                        <tr style="background: #fafafa;"><td style="padding: 12px 5px;">關卡二 (1.4)</td><td style="text-align: right; font-weight: bold;">{t2:.2f}</td></tr>
                    </table>

                    <div style="background: #fff9c4; padding: 20px; border-radius: 20px; border: 3px solid #fbc02d; margin-top: 10px;">
                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 15px; font-size: 19px;">🐰 兔子理財小學堂：買股心法</div>
                        
                        <div style="background: #fef9e7; padding: 15px; border-radius: 12px; margin-bottom: 18px; text-align: center; border: 1px dashed #fbc02d;">
                            <div style="color: #c92a2a; font-weight: bold; font-size: 17px;">核心：買比【法人成本】高一點點的股！</div>
                            <div style="color: #5d4037; font-size: 14px; margin-top: 5px; font-weight: bold;">低位盤整 + 股價推升 = 主力收貨完成</div>
                        </div>

                        <div style="text-align: center; color: #8d6e63; font-weight: bold; margin-bottom: 12px; font-size: 17px;">🎯 選股四原則實戰說明</div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #fbc02d;">
                                <div style="font-size: 15px; font-weight: bold; color: #c92a2a;">1. 強勢股 (趨勢領先)</div>
                                <div style="font-size: 13px; color: #666; margin-top: 4px;">股價必須站穩在<b>季線 (60MA)</b> 之上。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #fbc02d;">
                                <div style="font-size: 15px; font-weight: bold; color: #c92a2a;">2. 法人持續加碼 (籌碼靠山)</div>
                                <div style="font-size: 13px; color: #666; margin-top: 4px;">觀察外資、投信是否在股價盤整時<b>連續買超</b>。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #fbc02d;">
                                <div style="font-size: 15px; font-weight: bold; color: #c92a2a;">3. 多頭線型 (上升慣性)</div>
                                <div style="font-size: 13px; color: #666; margin-top: 4px;">利用 AI 偵測 <b>股價 > 月線 > 季線</b> 的排列。</div>
                            </div>
                            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #fbc02d;">
                                <div style="font-size: 15px; font-weight: bold; color: #c92a2a;">4. 現價離成本近 (獲利空間)</div>
                                <div style="font-size: 13px; color: #666; margin-top: 4px;">最理想的買點是<b>靠近法人平均成本</b>。</div>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card_html, height=1600, scrolling=True)
            else:
                st.error("❌ 抓取數據失敗。")
    except Exception as e:
        st.error(f"⚠️ 請檢查輸入內容格式是否正確。")
