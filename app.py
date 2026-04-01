import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components
import twstock

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔關卡價", page_icon="🎯", layout="centered")

# 2. 手機版美化介面
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #7b0099; color: white; font-weight: bold;
        font-size: 1.1em;
    }
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; }
    input { font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 仙兔關卡價查詢")

# 3. 輸入區 (優化：支援小數點後兩位)
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="2330")
with col2:
    # 修改 step=0.01 讓鍵盤支援兩位小數，format="%.2f" 顯示兩位
    cost = st.number_input("基準成本", value=1664.90, step=0.01, format="%.2f")

# 數字鍵盤補丁
components.html(
    """<script>
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => { 
        input.setAttribute('inputmode', 'decimal'); 
        input.setAttribute('pattern', '[0-9]*');
    });
    </script>""", height=0,
)

def get_analysis(sid):
    # A. 抓取中文名稱
    try:
        stock_info = twstock.codes.get(sid)
        name = stock_info.name if stock_info else sid
    except:
        name = sid

    # B. 抓取現價 (強化版爬蟲)
    price = None
    try:
        url = f"https://tw.stock.yahoo.com/quote/{sid}"
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 嘗試抓取 Yahoo 價格標籤 (包含漲、跌、平盤三種可能的 class)
        price_tag = soup.find('span', class_=lambda x: x and 'Fz(32px)' in x)
        if price_tag:
            price = float(price_tag.text.replace(',', ''))
    except:
        pass

    return name, price

if st.button("🚀 開始計算報告"):
    with st.spinner('數據同步中...'):
        stock_name, current_price = get_analysis(sid)
        
        if current_price:
            # 仙兔邏輯計算
            takeoff = round(cost * 1.04, 2)
            t1, t2, t3 = round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            
            # 狀態判斷
            if current_price < cost: status, color = "🟢 弱勢 (低於成本)", "normal"
            elif cost <= current_price < takeoff: status, color = "🟡 盤整 (站上成本)", "off"
            elif takeoff <= current_price < t1: status, color = "🚀 起飛 (過1.04)", "inverse"
            else: status, color = "🔥 強勢 (已達標)", "inverse"

            # 4. 顯示結果卡片
            st.divider()
            st.subheader(f"{stock_name} ({sid})")
            st.metric("當前現價", f"{current_price:.2f}", delta=status, delta_color=color)
            
            # 5. 數據表 (統一顯示到小數點後兩位)
            st.write("### 📏 關卡價參考表")
            res_data = [
                {"項目": "基準成本", "數值": f"{cost:.2f}"},
                {"項目": "起飛價 (1.04)", "數值": f"{takeoff:.2f}"},
                {"項目": "第一滿足 (1.2)", "數值": f"{t1:.2f}"},
                {"項目": "第二滿足 (1.4)", "數值": f"{t2:.2f}"},
                {"項目": "第三滿足 (1.7)", "數值": f"{t3:.2f}"}
            ]
            st.table(res_data)
        else:
            st.error(f"❌ 無法抓取 {sid} 的現價。請檢查網路或稍後再試。")

st.caption("數據來源：twstock & Yahoo | 邏輯：仙兔關卡價")
