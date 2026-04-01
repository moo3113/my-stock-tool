import streamlit as st
import requests
from bs4 import BeautifulSoup
import twstock

# 1. 基礎設定
st.set_page_config(page_title="仙兔分析儀", page_icon="🐰")

# 2. 簡單標題
st.title("🐰 仙兔波浪分析系統")
st.write("---")

# 3. 輸入區
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="1815")
with col2:
    cost_str = st.text_input("外資/法人成本", value="105.6")

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
                # 數據計算
                p104 = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost * 1.2, 2), round(cost * 1.4, 2), round(cost * 1.7, 2)
                
                # 🎯 神獸邏輯：成本數字 大於 現價的 1.7 倍
                is_god_beast = cost >= (price * 1.7)
                
                # 顯示股票頭部資訊
                st.subheader(f"📊 {name} ({sid})")
                
                # 顯示現價卡片
                st.metric("當前市場現價", f"{price:.2f}")

                # 4. 上古神獸警告 (使用原生警告元件)
                if is_god_beast:
                    st.warning("✨ **偵測到「上古神獸」**：輸入成本已超過現價 1.7 倍！建議改用【融資成本】重新計算。")

                # 5. 兔兔戰術建議 (使用原生訊息元件)
                if is_god_beast:
                    strategy = "📍 **上古神獸警報！** 成本與現價落差過大，建議改用【融資成本】計算。"
                elif price < cost:
                    strategy = "📍 **現價低於成本！** 法人還在盤整/收貨階段，建議耐心守候。"
                elif cost <= price < p104:
                    strategy = "📍 **處於起跑區。** 等待突破 1.04 倍關鍵點。"
                elif p104 <= price < t1:
                    strategy = "📍 **已突破 1.04！** 目標關卡一 (1.2)。注意 3-5 日盤整。"
                else:
                    strategy = "📍 **波浪行進中。** 請依關卡價觀察支撐與壓力。"
                
                st.info(strategy)

                # 6. 關卡數據表格 (使用標準 Dataframe)
                st.write("### 📏 關卡分析表")
                res_data = [
                    {"項目": "法人原始成本", "數值": f"{cost:.2f}"},
                    {"項目": "突破點 (1.04)", "數值": f"{p104:.2f}"},
                    {"項目": "關卡一 (1.2)", "數值": f"{t1:.2f}"},
                    {"項目": "關卡二 (1.4)", "數值": f"{t2:.2f}"},
                    {"項目": "關卡三 (1.7)", "數值": f"{t3:.2f}"}
                ]
                st.table(res_data)
                
                if is_god_beast:
                    st.caption("💡 備註：目前位階已達神獸級，上述關卡僅供參考，請優先參考融資成本。")

            else:
                st.error("❌ 無法獲取數據，請確認代號正確。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")

st.write("---")
st.caption("實戰穩定版 v5.0")
