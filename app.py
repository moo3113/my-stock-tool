import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components
import twstock

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
    }
    input { font-size: 1.2rem !important; border-radius: 10px !important; }
    .report-card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); margin-top: 20px; border: 1px solid #ffe3e3; }
    .report-header { background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center; }
    .report-table { width: 100%; border-collapse: collapse; }
    .report-table tr { border-bottom: 1px solid #fff0f0; }
    .report-table tr:nth-child(even) { background-color: #fafafa; }
    .report-label { padding: 12px 20px; color: #777; font-weight: 600; width: 55%; }
    .report-value { padding: 12px 20px; text-align: right; font-weight: bold; color: #fa5252; font-size: 1.1rem; }
    
    /* 上古神獸警告樣式 */
    .god-beast-alert {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #5d4037; padding: 15px; margin: 15px; border-radius: 15px;
        text-align: center; font-weight: bold; font-size: 0.95rem;
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.4);
        border: 1px solid #FF8C00;
    }
    .strategy-box { background-color: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 15px; border-radius: 8px; font-size: 0.9rem; color: #444; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔波浪分析系統")
st.caption("融入：波浪理論 & 神獸位階判斷 v4.1")

# 3. 輸入區
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="1815")
with col2:
    cost_str = st.text_input("外資/法人成本", value="105.6")

# 手機數字鍵盤補丁
components.html("""<script>
    const setNumberKeyboard = () => {
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('type', 'number');
            input.setAttribute('inputmode', 'decimal');
        });
    }
    setTimeout(setNumberKeyboard, 500);
</script>""", height=0)

def get_google_data(sid):
    for ex in ["TPE", "TWO"]:
        try:
            url = f"https://www.google.com/finance/quote/{sid}:{ex}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                price_tag = soup.select_one('div[data-last-price]')
                if price_tag:
                    price = float(price_tag['data-last-price'])
                    name_tag = soup.select_one('.zzDe30')
                    name = name_tag.text if name_tag else sid
                    return name, price
        except: continue
    return None, None

if st.button("🚀 執行波浪數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('同步數據中...'):
            name, price = get_google_data(sid)
            
            if price:
                # 核心計算
                p104 = round(cost * 1.04, 2)
                t1 = round(cost * 1.2, 2)
                t2 = round(cost * 1.4, 2)
                t3 = round(cost * 1.7, 2)
                
                # 🎯 核心邏輯修正：成本數字 大於 現價的 1.7 倍
                is_god_beast = cost >= (price * 1.7)
                
                # 戰術邏輯判斷
                if is_god_beast:
                    strategy = "📍 **上古神獸警報！** 成本與現價落差過大，建議改用【融資成本】計算。"
                    status, color = "✨ 神獸位階", "#d4a017"
                elif price < cost:
                    strategy = "📍 **現價低於成本！** 法人還在盤整/收貨階段，建議耐心守候。"
                    status, color = "🟢 盤整收貨", "#51cf66"
                elif cost <= price < p104:
                    strategy = "📍 **處於起跑區。** 等待突破 1.04 倍關鍵點。"
                    status, color = "🟡 蓄勢待發", "#fcc419"
                else:
                    strategy = "📍 **波浪行進中。** 請依關卡價觀察支撐與壓力。"
                    status, color = "#ff6b6b", "#ff6b6b"

                # 神獸金色警告勳章
                god_beast_html = f"""
                <div class="god-beast-alert">
                    ✨ 偵測到「上古神獸」✨<br>
                    輸入成本已超過現價 1.7 倍！建議改用【融資成本】。
                </div>
                """ if is_god_beast else ""

                report_html = f"""
                <div class="report-card">
                    <div class="report-header">
                        <div style="font-size: 1.8rem; font-weight: bold;">{name} ({sid})</div>
                    </div>
                    {god_beast_html}
                    <div style="padding: 25px; text-align: center;">
                        <div style="font-size: 0.8rem; color: #888; letter-spacing: 2px;">當前市場現價</div>
                        <div style="font-size: 3.5rem; font-weight: bold; color: {color}; line-height: 1.2;">{price:.2f}</div>
                        <div style="margin-top: 10px;">
                            <span style="padding: 6px 18px; border-radius: 20px; background: {color}; color: white; font-weight: bold; font-size: 0.9rem;">{status}</span>
                        </div>
                    </div>
                    <div class="strategy-box">{strategy}</div>
                    <table class="report-table">
                        <tr {"style='background-color:#fff9c4;'" if is_god_beast else ""}>
                            <td class="report-label">法人原始成本</td>
                            <td class="report-value">{cost:.2f}</td>
                        </tr>
                        <tr style="background-color: #fff9db;"><td class="report-label" style="color: #e67e22;">突破點 (1.04)</td><td class="report-value" style="color: #e67e22;">{p104:.2f}</td></tr>
                        <tr><td class="report-label">關卡一 (1.2高點)</td><td class="report-value">{t1:.2f}</td></tr>
                        <tr><td class="report-label">關卡二 (1.4高點)</td><td class="report-value">{t2:.2f}</td></tr>
                        <tr><td class="report-label">關卡三 (1.7高點)</td><td class="report-value">{t3:.2f}</td></tr>
                    </table>
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
            else:
                st.error("❌ 無法獲取數據，請確認代號正確。")
    except: st.error("⚠️ 請輸入正確的數字格式。")

st.write("---")
st.markdown("**🐰 仙兔選股四原則：**\n1. 優先選強勢股 | 2. 觀察法人持續加碼 | 3. 確認多頭線型 | 4. 現價比成本高一點或差不多為佳。")
st.caption("實戰版 v4.1 | 邏輯：當成本 > 現價x1.7 時提示改用融資成本")
