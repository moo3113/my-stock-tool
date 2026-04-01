import streamlit as st
import requests
from bs4 import BeautifulSoup
import twstock

# 1. 基礎設定
st.set_page_config(page_title="仙兔波浪分析儀", page_icon="🐰", layout="centered")

# 2. 標題
st.title("🐰 仙兔波浪分析系統")
st.markdown("---")

# 3. 輸入區
col1, col2 = st.columns(2)
with col1:
    sid = st.text_input("股票代號", value="1815")
with col2:
    cost_str = st.text_input("外資/法人成本", value="105.6")

def get_google_data(sid):
    """從 Google Finance 抓取現價與名稱"""
    for ex in ["TPE", "TWO"]:
        try:
            url = f"https://www.google.com/finance/quote/{sid}:{ex}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                price_tag = soup.select_one('div[data-last-price]')
                name_tag = soup.select_one('.zzDe30')
                if price_tag:
                    return name_tag.text if name_tag else sid, float(price_tag['data-last-price'])
        except: continue
    return sid, None

if st.button("🚀 執行波浪數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('同步數據中...'):
            # 優先從 twstock 抓中文名
            try:
                stock_info = twstock.codes.get(sid)
                name = stock_info.name if stock_info else sid
            except:
                name = sid
            
            # 從 Google 抓現價
            g_name, price = get_google_data(sid)
            if name == sid: name = g_name 

            if price:
                # 數據計算
                p104 = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost * 1.2, 2), round(cost * 1.4, 2), round(cost * 1.7, 2)
                
                # 🎯 神獸邏輯：成本數字 大於 現價的 1.7 倍
                is_god_beast = cost >= (price * 1.7)
                
                # A. 顯示結果頭部
                st.subheader(f"📊 {name} ({sid})")
                st.metric("當前市場現價", f"{price:.2f}")

                # B. 上古神獸警告
                if is_god_beast:
                    st.warning(f"✨ **偵測到「上古神獸」**：輸入成本 {cost} 已超過現價 1.7 倍！建議改用【融資成本】重新計算。")

                # C. 兔兔戰術建議
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
                
                with st.chat_message("user", avatar="🐰"):
                    st.write(strategy)

                # D. 關卡數據表格
                st.write("### 📏 關卡分析表")
                res_data = [
                    {"項目": "法人原始成本", "數值": f"{cost:.2f}"},
                    {"項目": "突破點 (1.04)", "數值": f"{p104:.2f}"},
                    {"項目": "關卡一 (1.2高點)", "數值": f"{t1:.2f}"},
                    {"項目": "關卡二 (1.4高點)", "數值": f"{t2:.2f}"},
                    {"項目": "關卡三 (1.7神獸點)", "數值": f"{t3:.2f}"}
                ]
                st.table(res_data)
                
                # E. 融入圖片中的：選股四原則
                st.success("""
                **🐰 兔子理財：選股四原則**
                1. **強勢股**：優先選擇有動能的標的。
                2. **法人持續加碼**：籌碼面有支撐。
                3. **多頭線型**：技術面趨勢向上。
                4. **現價比成本高或差不多**：避免追高，回檔成本區附近最安全。
                """)

            else:
                st.error("❌ 無法獲取數據，請確認代號正確。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")

st.write("---")
st.caption("實戰版 v5.2 | 完整融入兔子理財心法")
