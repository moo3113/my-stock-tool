import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components
import twstock
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔分析儀-除錯版", page_icon="🐰", layout="centered")

# 2. CSS 樣式 (保持原樣)
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { width: 100%; border-radius: 15px; height: 3.8em; background: linear-gradient(135deg, #ff6b6b, #f06595); color: white; font-weight: bold; }
    .report-card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); margin-top: 20px; border: 1px solid #ffe3e3; }
    .report-header { background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center; }
    .report-table { width: 100%; border-collapse: collapse; }
    .report-table tr { border-bottom: 1px solid #fff0f0; }
    .report-label { padding: 12px 20px; color: #777; font-weight: 600; width: 55%; }
    .report-value { padding: 12px 20px; text-align: right; font-weight: bold; color: #fa5252; font-size: 1.1rem; }
    .strategy-box { background-color: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 15px; border-radius: 8px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔波浪分析系統")

# 3. 輸入區
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="1815")
with col2:
    cost_str = st.text_input("外資/法人成本", value="105.6")

# 數字鍵盤補丁
components.html("""<script>
    const setNumberKeyboard = () => {
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => { input.setAttribute('type', 'number'); input.setAttribute('inputmode', 'decimal'); });
    }
    setTimeout(setNumberKeyboard, 500);
</script>""", height=0)

if st.button("🚀 執行分析"):
    try:
        cost = float(cost_str)
        with st.spinner('正在從資料庫抓取數據...'):
            # --- 強化版抓取邏輯 ---
            ticker_list = [f"{sid}.TW", f"{sid}.TWO"]
            price, ma60, name = None, None, None
            
            for t_code in ticker_list:
                tk = yf.Ticker(t_code)
                df = tk.history(period="100d")
                if not df.empty:
                    price = df['Close'].iloc[-1]
                    ma60 = df['Close'].rolling(window=60).mean().iloc[-1]
                    break
            
            # 抓中文名
            try:
                name = twstock.codes[sid].name
            except:
                name = sid

            if price and ma60:
                # 仙兔波浪計算
                p104 = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost * 1.2, 2), round(cost * 1.4, 2), round(cost * 1.7, 2)
                is_god_beast = price >= t3
                
                # 判定狀態
                if price < cost: status, color = "🟢 盤整收貨", "#51cf66"
                elif price < p104: status, color = "🟡 蓄勢待發", "#fcc419"
                elif price < t1: status, color = "🚀 突破起飛", "#ff922b"
                else: status, color = "🔥 強勢波浪", "#ff6b6b"

                # 4. 輸出 HTML (這一段如果沒跑出來，代表程式當在上面了)
                report_html = f"""
                <div class="report-card">
                    <div class="report-header"><div style="font-size: 1.8rem; font-weight: bold;">{name} ({sid})</div></div>
                    <div style="padding: 25px; text-align: center;">
                        <div style="font-size: 3.5rem; font-weight: bold; color: {color};">{price:.2f}</div>
                        <span style="padding: 6px 18px; border-radius: 20px; background: {color}; color: white; font-weight: bold;">{status}</span>
                    </div>
                    <table class="report-table">
                        <tr style="background-color: #fff0f0;"><td class="report-label">季線 (60MA)</td><td class="report-value">{ma60:.2f}</td></tr>
                        <tr><td class="report-label">法人原始成本</td><td class="report-value">{cost:.2f}</td></tr>
                        <tr style="background-color: #fff9db;"><td class="report-label">突破點 (1.04)</td><td class="report-value">{p104:.2f}</td></tr>
                        <tr><td class="report-label">關卡一 (1.2)</td><td class="report-value">{t1:.2f}</td></tr>
                        <tr {"style='background-color:#fff9c4;'" if is_god_beast else ""}><td class="report-label">關卡三 (1.7神獸點)</td><td class="report-value">{t3:.2f}</td></tr>
                    </table>
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
            else:
                st.error(f"❌ 抓不到 {sid} 的歷史數據。請確認代號正確，或檢查網路。")
                
    except Exception as e:
        st.error(f"⚠️ 程式執行出錯: {e}")

st.caption("v3.7 Debug Mode")
