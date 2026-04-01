import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔關卡價", page_icon="📈", layout="centered")

# 2. 針對手機美化介面 (自定義 CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #7b0099; 
        color: white; 
        font-weight: bold;
        font-size: 1.1em;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; }
    /* 讓輸入框在手機上看起來更清楚 */
    input { font-size: 1.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 仙兔關卡價查詢")

# 3. 輸入區 (使用 Columns 讓手機排版更緊湊)
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="2330")
with col2:
    # 這裡設定 format 與 step，輔助手機識別為數字
    cost = st.number_input("基準成本", value=1800.0, step=0.1, format="%.1f")

# --- 🚀 手機純數字鍵盤強化補丁 (JavaScript) ---
components.html(
    """
    <script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        // 針對股票代號與成本，強制開啟數字模式
        input.setAttribute('inputmode', 'decimal');
        input.setAttribute('pattern', '[0-9]*');
    });
    </script>
    """,
    height=0,
)

if st.button("🚀 開始計算分析"):
    try:
        # 抓取 Yahoo 奇摩股市數據
        url = f"https://tw.stock.yahoo.com/quote/{sid}"
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 抓取中文名稱 (從標題解析)
        title_text = soup.title.string
        stock_name = title_text.split('(')[0].strip() if '(' in title_text else sid
        
        # 抓取現價
        price_tag = soup.select_one('span[class*="Fz(32px)"]')
        if price_tag:
            price = float(price_tag.text.replace(',', ''))
            
            # 仙兔倍數邏輯計算
            takeoff = round(cost * 1.04, 2)
            t1 = round(cost * 1.2, 2)
            t2 = round(cost * 1.4, 2)
            t3 = round(cost * 1.7, 2)
            
            # 狀態判斷
            if price < cost: 
                status, color = "🟢 弱勢 (低於成本)", "normal"
            elif cost <= price < takeoff: 
                status, color = "🟡 盤整 (站上成本)", "off"
            elif takeoff <= price < t1: 
                status, color = "🚀 起飛 (過1.04)", "inverse"
            else: 
                status, color = "🔥 強勢 (已達標)", "inverse"

            # 4. 顯示結果卡片
            st.divider()
            st.subheader(f"{stock_name} ({sid})")
            st.metric("當前現價", f"{price:.2f}", delta=status, delta_color=color)
            
            # 5. 數據表 (採用方法 B：保留一位小數)
            st.write("### 📏 關卡價參考表")
            res_data = [
                {"項目": "基準成本", "數值": f"{cost:.1f}"},
                {"項目": "起飛價 (1.04)", "數值": f"{takeoff:.1f}"},
                {"項目": "第一滿足 (1.2)", "數值": f"{t1:.1f}"},
                {"項目": "第二滿足 (1.4)", "數值": f"{t2:.1f}"},
                {"項目": "第三滿足 (1.7)", "數值": f"{t3:.1f}"}
            ]
            st.table(res_data)
        else:
            st.error("❌ 抓不到價格，請確認代號是否正確。")
    except Exception as e:
        st.error(f"系統錯誤: {e}")

st.caption("數據來源：Yahoo 奇摩股市 | 邏輯：仙兔關卡價")
