import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
import twstock
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔波浪分析儀", page_icon="🐰", layout="centered")

# 2. 針對手機優化 CSS
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.8em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; font-size: 1.1em; border: none;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.3);
    }
    input { font-size: 1.2rem !important; border-radius: 10px !important; }
    
    .report-card {
        background: white; border-radius: 20px; overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); margin-top: 20px;
        border: 1px solid #ffe3e3;
    }
    .report-header {
        background: linear-gradient(135deg, #ff8787, #ff6b6b);
        color: white; padding: 20px; text-align: center;
    }
    .report-table { width: 100%; border-collapse: collapse; }
    .report-table tr { border-bottom: 1px solid #fff0f0; }
    .report-table tr:nth-child(even) { background-color: #fafafa; }
    .report-label { padding: 12px 20px; color: #777; font-weight: 600; width: 55%; }
    .report-value { padding: 12px 20px; text-align: right; font-weight: bold; color: #fa5252; font-size: 1.1rem; }
    
    .god-beast-alert {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #5d4037; padding: 15px; margin: 15px; border-radius: 15px;
        text-align: center; font-weight: bold; font-size: 0.95rem;
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.4);
        border: 1px solid #FF8C00;
    }
    
    .strategy-box {
        background-color: #fff5f5; border-left: 5px solid #ff6b6b;
        padding: 15px; margin: 15px; border-radius: 8px; font-size: 0.9rem; color: #444;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔波浪分析系統")
st.caption("融入：法人成本波浪理論 & 神獸偵測 v3.6")

# 3. 輸入區
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="1815")
with col2:
    cost_str = st.text_input(
        "外資/法人成本", 
        value="105.6", 
        help="注意：若股價超過 1.7 倍即為上古神獸，建議改用融資成本計算。"
    )

# 手機數字鍵盤補丁
components.html(
    """<script>
    const setNumberKeyboard = () => {
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('type', 'number');
            input.setAttribute('inputmode', 'decimal');
        });
    }
    setTimeout(setNumberKeyboard, 500);
    </script>""", height=0,
)

def get_stock_data(sid):
    try:
        for suffix in [".TW", ".TWO"]:
            ticker = yf.Ticker(f"{sid}{suffix}")
            hist = ticker.history(period="100d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                ma60 = hist['Close'].rolling(window=60).mean().iloc[-1]
                stock_info = twstock.codes.get(sid)
                name = stock_info.name if stock_info else sid
                return name, price, ma60
    except: pass
    return None, None, None

if st.button("🚀 執行波浪數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('波浪數據計算中...'):
            name, price, ma60 = get_stock_data(sid)
            
            if price:
                p104 = round(cost * 1.04, 2)
                t1 = round(cost * 1.2, 2)
                t2 = round(cost * 1.4, 2)
                t3 = round(cost * 1.7, 2)
                is_god_beast = price >= t3
                
                if price < cost:
                    strategy = "📍 **現價低於成本！** 法人還在盤整/收貨階段，建議耐心守候。"
                    status, color = "🟢 盤整收貨", "#51cf66"
                elif cost <= price < p104:
                    strategy = "📍 **處於起跑區。** 等待突破 1.04 倍關鍵點。"
                    status, color = "🟡 蓄勢待發", "#fcc419"
                elif p104 <= price < t1:
                    strategy = "📍 **已突破 1.04！** 目標關卡一 (1.2)。注意 3-5 日盤整。"
                    status, color = "🚀 突破起飛", "#ff922b"
                elif t1 <= price < t2:
                    strategy = "📍 **站上關卡一。** 朝關卡二 (1.4) 前進，盤整期會較久。"
                    status, color = "🔥 強勢波浪", "#ff6b6b"
                else:
                    strategy = "📍 **警戒：已達高標位階！** 建議改用【融資成本】重新計算波浪。"
                    status, color = "⚠️ 高檔警戒", "#e63946"

                god_beast_html = f"""
                <div class="god-beast-alert">
                    ✨ 偵測到「上古神獸」✨<br>
                    漲幅已超過 1.7 倍！請改用【融資成本】重新計算。
                </div>
                """ if is_god_beast else ""

                report_html = f"""
                <div class="report-card">
                    <div class="report-header">
                        <div style="font-size: 1.8rem; font-weight: bold;">{name} ({sid})</div>
                    </div>
                    {god_beast_html}
                    <div style="padding: 25px; text-align: center;">
                        <div style="font-size: 0.8rem; color: #888; letter-spacing: 2px;">當前市場位階</div>
                        <div style="font-size: 3.5rem; font-weight: bold; color: {color}; line-height: 1.2;">{price:.2f}</div>
                        <div style="margin-top: 10px;">
                            <span style="padding: 6px 18px; border-radius: 20px; background: {color}; color: white; font-weight: bold; font-size: 0.9rem;">{status}</span>
                        </div>
                    </div>
                    <div class="strategy-box">{strategy}</div>
                    <table class="report-table">
                        <tr style="background-color: #fff0f0;"><td class="report-label" style="color:#f06595;">季線 (60MA)位階</td><td class="report-value" style="color:#f06595;">{ma60:.2f}</td></tr>
                        <tr><td class="report-label">法人原始成本</td><td class="report-value">{cost:.2f}</td></tr>
                        <tr style="background-color: #fff9db;"><td class="report-label" style="color: #e67e22;">突破點 (1.04)</td><td class="report-value" style="color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td class="report-label">關卡一 (1.2高點)</td><td class="report-value">{t1:.2f}</td></tr>
                        <tr><td class="report-label">關卡二 (1.4高點)</td><td class="report-value">{t2:.2f}</td></tr>
                        <tr {"style='background-color:#fff9c4;'" if is_god_beast else ""}>
                            <td class="report-label">關卡三 (1.7神獸點)<br><small style="color:#888; font-weight:normal;">建議改用融資成本</small></td>
                            <td class="report-value">{t3:.2f}</td>
                        </tr>
                    </table>
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
            else:
                st.error("❌ 無法抓取數據。請檢查網路或代號。")
    except Exception as e: st.error(f"⚠️ 請輸入正確的數字格式。")

st.write("---")
st.markdown("**🐰 仙兔選股四原則：**\n1. 優先選強勢股 | 2. 觀察法人持續加碼 | 3. 確認多頭線型 | 4. 現價比成本高一點或差不多為佳。")
st.caption("數據來源：yfinance & twstock | 實戰版 v3.6")
