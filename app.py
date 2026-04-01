import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
import twstock
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔關卡價", page_icon="🎯", layout="centered")

# 2. 針對手機優化 CSS (加入季線與關卡美化)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.8em; 
        background: linear-gradient(135deg, #7b0099, #9d4edd); 
        color: white; font-weight: bold; font-size: 1.1em; border: none;
        box-shadow: 0 4px 15px rgba(123, 0, 153, 0.3);
    }
    input { font-size: 1.2rem !important; border-radius: 10px !important; }
    
    /* 專業報告卡片 */
    .report-card {
        background: white; border-radius: 20px; overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-top: 20px;
        font-family: 'Microsoft JhengHei', sans-serif;
    }
    .report-header {
        background: linear-gradient(135deg, #2c3e50, #4ca1af);
        color: white; padding: 20px; text-align: center;
    }
    .report-table { width: 100%; border-collapse: collapse; }
    .report-table tr { border-bottom: 1px solid #f2f2f2; }
    .report-table tr:nth-child(even) { background-color: #fafafa; }
    .report-label { padding: 12px 20px; color: #555; font-weight: 600; width: 50%; }
    .report-value { padding: 12px 20px; text-align: right; font-weight: bold; color: #2c3e50; font-size: 1.1rem; }
    
    /* 特殊列顏色 */
    .ma-row { background-color: #eef7ff !important; }
    .ma-label { color: #0056b3; }
    .takeoff-row { background-color: #fff5f5 !important; }
    .takeoff-label { color: #e63946; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 仙兔分析：關卡價 + 季線")

# 3. 輸入區 (強制觸發數字鍵盤)
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="2330", key="sid_input")
with col2:
    cost_str = st.text_input("基準成本", value="1664.90", key="cost_input")

# 手機數字鍵盤補丁
components.html(
    """
    <script>
    const setNumberKeyboard = () => {
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('type', 'number');
            input.setAttribute('inputmode', 'decimal');
        });
    }
    setTimeout(setNumberKeyboard, 500);
    </script>
    """, height=0,
)

def get_stock_data(sid):
    """獲取現價、中文名並計算 60MA"""
    try:
        # 優先嘗試 .TW (上市)，不行再試 .TWO (上櫃)
        for suffix in [".TW", ".TWO"]:
            ticker = yf.Ticker(f"{sid}{suffix}")
            # 抓取 100 天數據確保夠算 60MA
            hist = ticker.history(period="100d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                # 計算 60MA (季線)
                ma60 = hist['Close'].rolling(window=60).mean().iloc[-1]
                # 抓取中文名
                stock_info = twstock.codes.get(sid)
                name = stock_info.name if stock_info else sid
                return name, price, ma60
    except:
        pass
    return None, None, None

if st.button("🚀 生成專業分析報告"):
    try:
        cost = float(cost_str)
        with st.spinner('數據計算中...'):
            name, price, ma60 = get_stock_data(sid)
            
            if price:
                # 仙兔邏輯計算
                takeoff = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                
                # 位階判斷
                ma_status = "📈 站上季線" if price >= ma60 else "📉 低於季線"
                if price < cost: status, color = "🟢 弱勢 (低於成本)", "#27ae60"
                elif cost <= price < takeoff: status, color = "🟡 盤整 (站上成本)", "#f39c12"
                elif takeoff <= price < t1: status, color = "🚀 起飛 (過1.04)", "#e67e22"
                else: status, color = "🔥 強勢 (已達標)", "#e63946"

                # 4. 輸出精美 HTML 報告
                report_html = f"""
                <div class="report-card">
                    <div class="report-header">
                        <div style="font-size: 1.8rem; font-weight: bold; letter-spacing: 2px;">{name} ({sid})</div>
                    </div>
                    <div style="padding: 25px; text-align: center; border-bottom: 2px solid #f8f9fa;">
                        <div style="font-size: 0.9rem; color: #888;">目前現價</div>
                        <div style="font-size: 3.5rem; font-weight: bold; color: {color}; line-height: 1;">{price:.2f}</div>
                        <div style="margin: 15px 0;">
                            <span style="padding: 6px 15px; border-radius: 20px; background: {color}; color: white; font-weight: bold; font-size: 0.9rem;">{status}</span>
                        </div>
                        <div style="color: #444; font-weight: bold;">{ma_status}</div>
                    </div>
                    <table class="report-table">
                        <tr class="ma-row"><td class="report-label ma-label">季線 (60MA)</td><td class="report-value ma-label">{ma60:.2f}</td></tr>
                        <tr><td class="report-label">基準成本</td><td class="report-value">{cost:.2f}</td></tr>
                        <tr class="takeoff-row"><td class="report-label takeoff-label">起飛價 (1.04)</td><td class="report-value takeoff-label">{takeoff:.2f}</td></tr>
                        <tr><td class="report-label">第一滿足 (1.2)</td><td class="report-value">{t1:.2f}</td></tr>
                        <tr><td class="report-label">第二滿足 (1.4)</td><td class="report-value">{t2:.2f}</td></tr>
                        <tr><td class="report-label">第三滿足 (1.7)</td><td class="report-value">{t3:.2f}</td></tr>
                    </table>
                    <div style="background: #f8f9fa; padding: 15px; text-align: center; font-size: 0.8rem; color: #bbb;">
                        系統數據同步：yfinance & twstock
                    </div>
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
            else:
                st.error("❌ 無法抓取即時數據，請確認代號正確。")
    except ValueError:
        st.error("⚠️ 請輸入正確的數字格式。")

st.caption("Designed for Mobile | v2.5")
