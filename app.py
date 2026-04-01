import streamlit as st
import requests
from bs4 import BeautifulSoup

# 設定手機網頁標題
st.set_page_config(page_title="仙兔關卡價", page_icon="📈", layout="centered")

# 美化手機介面 CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #7b0099; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 仙兔關卡價查詢")

# 輸入區
sid = st.text_input("請輸入股票代號 (如 2330)", value="2330")
cost = st.number_input("請輸入基準成本", value=1800.0, step=0.1)

if st.button("立即分析"):
    try:
        # 1. 抓取 Yahoo 數據
        url = f"https://tw.stock.yahoo.com/quote/{sid}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        title_text = soup.title.string
        stock_name = title_text.split('(')[0].strip() if '(' in title_text else sid
        
        price_tag = soup.select_one('span[class*="Fz(32px)"]')
        if price_tag:
            price = float(price_tag.text.replace(',', ''))
            
            # 2. 邏輯計算
            takeoff = round(cost * 1.04, 2)
            t1, t2, t3 = round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
            
            # 3. 狀態判斷
            if price < cost: status, color = "🟢 弱勢 (低於成本)", "green"
            elif cost <= price < takeoff: status, color = "🟡 盤整 (站上成本)", "orange"
            elif takeoff <= price < t1: status, color = "🚀 起飛 (過1.04)", "red"
            else: status, color = "🔥 強勢 (已達標)", "red"

            # 4. 顯示結果卡片
            st.success(f"### {stock_name} ({sid})")
            st.metric("當前現價", f"{price:.2f}", delta=status)
            
            # 5. 直式數據表
            st.write("---")
            res_df = {
                "項目": ["基準成本", "起飛價 (1.04)", "第一滿足 (1.2)", "第二滿足 (1.4)", "第三滿足 (1.7)"],
                "數值": [cost, takeoff, t1, t2, t3]
            }
            st.table(res_df)
        else:
            st.error("❌ 找不到股價資料，請檢查代號。")
    except Exception as e:
        st.error(f"錯誤: {e}")

st.caption("數據來源：Yahoo 奇摩股市 | 邏輯：仙兔關卡價")

