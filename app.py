import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import streamlit.components.v1 as components

# 1. 基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 2. 標題
st.title("🐰 仙兔 AI 波浪分析系統")
st.markdown("---")

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
        inputs.forEach(input => {
            input.setAttribute('type', 'number');
            input.setAttribute('inputmode', 'decimal');
        });
    }
    setTimeout(setNumberKeyboard, 500);
</script>""", height=0)

def get_comprehensive_data(sid):
    name, price, ma60 = sid, None, None
    try:
        stock_info = twstock.codes.get(sid)
        if stock_info: name = stock_info.name
    except: pass
    for suffix in [".TW", ".TWO"]:
        try:
            ticker = yf.Ticker(f"{sid}{suffix}")
            df = ticker.history(period="100d")
            if not df.empty:
                price = df['Close'].iloc[-1]
                ma60 = df['Close'].rolling(window=60).mean().iloc[-1]
                break
        except: continue
    return name, price, ma60

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('AI 正在計算波浪與位階建議...'):
            name, price, ma60 = get_comprehensive_data(sid)

            if price and ma60:
                # 數據計算
                p104 = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost * 1.2, 2), round(cost * 1.4, 2), round(cost * 1.7, 2)
                is_god_beast = cost >= (price * 1.7)
                
                # A. 顯示結果頭部
                st.subheader(f"📊 {name} ({sid})")
                
                col_a, col_b = st.columns(2)
                col_a.metric("當前現價", f"{price:.2f}")
                col_b.metric("季線 (60MA)", f"{ma60:.2f}", delta=f"{price-ma60:.2f}")

                # B. 上古神獸警告
                if is_god_beast:
                    st.warning(f"⚠️ **AI 神獸偵測警告**：成本 {cost} 已遠高於現價 1.7 倍！波浪起點已完全失真，AI 建議立即改用【融資成本】重新計算。")

                # C. 兔兔戰術建議
                if is_god_beast:
                    strategy = "📍 **操作重點：** 原始波浪已失效，請更換參考成本。"
                elif price < cost:
                    strategy = "📍 **操作重點：** 法人成本防線下方，目前為「相對安全區」，建議分批佈局。"
                elif cost <= price < p104:
                    strategy = "📍 **操作重點：** 盤整蓄勢中。若能站穩 1.04 倍 ({}) 則有機會發動。".format(p104)
                elif p104 <= price < t1:
                    strategy = "📍 **操作重點：** 突破起飛中。目標 1.2 關卡 ({})，注意短線回檔。".format(t1)
                else:
                    strategy = "📍 **操作重點：** 強勢波段行進中。已接近高位關卡，嚴禁追高。"
                
                with st.chat_message("user", avatar="🐰"):
                    st.write(strategy)

                # D. 🤖 AI 智慧分析建議 (升級版)
                st.info("🤖 **AI 智慧分析建議**")
                advice = []
                
                # 1. 趨勢位階
                if price > ma60:
                    advice.append("📈 **趨勢確認**：現價在季線之上，趨勢呈現多頭，適合持股或順勢操作。")
                else:
                    advice.append("📉 **趨勢警戒**：現價在季線之下，屬於空頭整理格局，不宜大注。")
                
                # 2. 獲利/回檔空間
                if price < p104:
                    advice.append("💎 **佈局建議**：目前處於法人成本附近，風險相對較低，可設定分批進場點。")
                elif price > t2:
                    advice.append("🔥 **過熱警訊**：股價已大漲超過 1.4 倍關卡，根據大數據，回檔壓力漸增，AI 建議分批落袋為安。")
                
                # 3. 關鍵支撐
                dist_to_ma60 = ((price - ma60) / ma60) * 100
                if dist_to_ma60 > 15:
                    advice.append("🚨 **正乖離過大**：現價與季線距離超過 15% ({:.1f}%)，隨時可能出現技術性修正。".format(dist_to_ma60))
                
                st.markdown("\n".join([f"- {a}" for a in advice]))

                # E. 關卡數據表格
                st.write("### 📏 完整關卡分析報告")
                res_data = [
                    {"項目": "季線 (60MA)", "數值": f"{ma60:.2f}"},
                    {"項目": "法人原始成本", "數值": f"{cost:.2f}"},
                    {"項目": "突破點 (1.04)", "數值": f"{p104:.2f}"},
                    {"項目": "關卡一 (1.2高點)", "數值": f"{t1:.2f}"},
                    {"項目": "關卡二 (1.4高點)", "數值": f"{t2:.2f}"},
                    {"項目": "關卡三 (1.7神獸點)", "數值": f"{t3:.2f}"}
                ]
                st.table(res_data)
                
                # F. 選股四原則
                st.success("""
                **🐰 兔子理財：選股四原則**
                1. **強勢股**：優先選擇有動能的標的。
                2. **法人持續加碼**：籌碼面有支撐。
                3. **多頭線型**：技術面趨勢向上。
                4. **現價比成本高或差不多**：回檔成本區附近最安全。
                """)

            else:
                st.error("❌ 抓取不到數據。請確認代號正確 (例如: 1815)。")
    except Exception as e:
        st.error(f"⚠️ AI 計算出錯: {e}")

st.write("---")
st.caption("AI 智慧分析版 v7.5 | 整合乖離率與波浪建議")
