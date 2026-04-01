import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import streamlit.components.v1 as components

# 1. 介面基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 2. 標題與版面美化
st.title("🐰 仙兔 AI 波浪分析系統")
st.caption("實戰智慧版 v8.0 | 整合神獸、波浪與 AI 筆記")
st.markdown("---")

# 3. 輸入區
with st.container():
    c1, c2 = st.columns(2)
    sid = c1.text_input("股票代號", value="1815")
    cost_str = c2.text_input("外資/法人成本", value="105.6")

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

def get_data(sid):
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

if st.button("🚀 執行 AI 數據分析", use_container_width=True):
    try:
        cost = float(cost_str)
        with st.spinner('AI 正在計算波浪位階...'):
            name, price, ma60 = get_data(sid)

            if price and ma60:
                # 數據計算
                p104 = round(cost * 1.04, 2)
                t1, t2, t3 = round(cost * 1.2, 2), round(cost * 1.4, 2), round(cost * 1.7, 2)
                
                # 🎯 神獸邏輯：成本數字 大於 現價的 1.7 倍
                is_god_beast = cost >= (price * 1.7)
                
                # A. 顯示結果頭部
                st.subheader(f"📊 {name} ({sid})")
                
                m1, m2 = st.columns(2)
                m1.metric("當前現價", f"{price:.2f}")
                m2.metric("季線 (60MA)", f"{ma60:.2f}", delta=f"{price-ma60:.2f}")

                # B. 上古神獸警告
                if is_god_beast:
                    st.warning(f"⚠️ **AI 神獸偵測警告**：成本 {cost} 已遠高於現價 1.7 倍！建議改用【融資成本】重新計算。")

                # C. 兔兔戰術建議
                if is_god_beast:
                    strategy = "📍 **操作重點：** 原始波浪已失效，建議改用融資成本重新抓波浪。"
                elif price < cost:
                    strategy = "📍 **操作重點：** 現價低於成本，法人盤整收貨中，適合分批佈局。"
                elif cost <= price < p104:
                    strategy = "📍 **操作重點：** 蓄勢待發！準備挑戰 1.04 突破點 ({})。".format(p104)
                elif p104 <= price < t1:
                    strategy = "📍 **操作重點：** 突破起飛中！目標 1.2 關卡 ({})。".format(t1)
                else:
                    strategy = "📍 **操作重點：** 強勢波段，注意 {} 之上的壓力，嚴禁追高。".format(t2)
                
                with st.chat_message("user", avatar="🐰"):
                    st.write(strategy)

                # D. 🤖 AI 智慧分析建議
                with st.expander("🤖 查看 AI 智慧分析建議", expanded=True):
                    advice = []
                    if price > ma60:
                        advice.append("📈 **趨勢**：多頭格局（現價 > 季線），適合持股。")
                    else:
                        advice.append("📉 **趨勢**：空頭整理（現價 < 季線），不宜過度加碼。")
                    
                    dist_to_ma60 = ((price - ma60) / ma60) * 100
                    if dist_to_ma60 > 15:
                        advice.append(f"🚨 **警告**：正乖離率高達 {dist_to_ma60:.1f}%，隨時有修正風險。")
                    
                    if price < p104:
                        advice.append("💎 **機會**：目前位階接近法人成本，屬於相對安全區。")
                    
                    for a in advice:
                        st.markdown(f"- {a}")

                # E. 關卡數據表格
                st.write("### 📏 完整關卡分析報告")
                df_res = pd.DataFrame({
                    "項目": ["季線 (60MA)", "法人原始成本", "突破點 (1.04)", "關卡一 (1.2)", "關卡二 (1.4)", "關卡三 (1.7)"],
                    "數值": [f"{ma60:.2f}", f"{cost:.2f}", f"{p104:.2f}", f"{t1:.2f}", f"{t2:.2f}", f"{t3:.2f}"]
                })
                st.table(df_res)
                
                # F. 選股四原則
                st.success("""
                **🐰 兔子理財：選股四原則**
                1. **強勢股**：優先選擇有動能的標的。
                2. **法人持續加碼**：籌碼面有支撐。
                3. **多頭線型**：技術面趨勢向上。
                4. **現價比成本高或差不多**：回檔成本區附近最安全。
                """)

            else:
                st.error("❌ 抓取不到數據。請確認代號正確。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")

st.write("---")
st.caption("實戰智慧版 v8.0 | 穩定架構")
