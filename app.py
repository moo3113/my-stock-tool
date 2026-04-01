import streamlit as st
import yfinance as yf
import twstock
import pandas as pd
import streamlit.components.v1 as components

# 1. 網頁基礎設定
st.set_page_config(page_title="仙兔 AI 分析儀", page_icon="🐰", layout="centered")

# 2. 隱藏原生多餘元件 (讓畫面更像 App)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; 
        background: linear-gradient(135deg, #ff6b6b, #f06595); 
        color: white; font-weight: bold; border: none;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐰 仙兔 AI 波浪分析系統")

# 3. 輸入區
c1, c2 = st.columns(2)
sid = c1.text_input("股票代號", value="1815")
cost_str = c2.text_input("外資/法人成本", value="105.6")

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

if st.button("🚀 執行 AI 數據分析"):
    try:
        cost = float(cost_str)
        with st.spinner('正在繪製精美分析報告...'):
            name, price, ma60 = get_data(sid)

            if price and ma60:
                # 數據計算
                p104, t1, t2, t3 = round(cost*1.04, 2), round(cost*1.2, 2), round(cost*1.4, 2), round(cost*1.7, 2)
                is_god_beast = cost >= (price * 1.7)
                
                # AI 邏輯判定
                if price < cost: 
                    strategy, color = "📍 現價低於成本，法人收貨中，適合分批低接。", "#51cf66"
                elif price < p104: 
                    strategy, color = "📍 處於起跑區，站穩 1.04 突破點後即起飛。", "#fcc419"
                elif price < t1: 
                    strategy, color = "📍 突破起飛中！目標 1.2 關卡，注意短線回檔。", "#ff922b"
                else: 
                    strategy, color = "📍 強勢波段行進中，注意高位壓力，嚴禁追高。", "#ff6b6b"

                # 神獸警告 HTML
                god_beast_html = f'''
                <div style="background: linear-gradient(135deg, #FFD700, #FFA500); color: #5d4037; padding: 15px; margin: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 14px; border: 1px solid #FF8C00;">
                    ✨ 偵測到「上古神獸」✨<br>輸入成本已超過現價 1.7 倍！建議改用【融資成本】。
                </div>
                ''' if is_god_beast else ""

                # AI 筆記內容
                ai_note = f"📈 趨勢偏多，股價在季線之上。" if price > ma60 else "📉 趨勢偏弱，股價在季線之下。"
                if ((price - ma60) / ma60) > 0.15: ai_note += "<br>🚨 正乖離過大，注意修正風險。"

                # 🚀 終極精美 HTML 封裝
                full_card = f'''
                <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #fffafb; padding: 5px;">
                    <div style="background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #ffe3e3;">
                        <div style="background: linear-gradient(135deg, #ff8787, #ff6b6b); color: white; padding: 20px; text-align: center;">
                            <div style="font-size: 22px; font-weight: bold;">{name} ({sid})</div>
                        </div>
                        
                        {god_beast_html}

                        <div style="padding: 20px; text-align: center;">
                            <div style="font-size: 12px; color: #888; letter-spacing: 2px; margin-bottom: 5px;">當前市場現價 / 季線位階</div>
                            <div style="display: flex; justify-content: space-around; align-items: center;">
                                <div>
                                    <div style="font-size: 38px; font-weight: bold; color: {color};">{price:.2f}</div>
                                    <div style="font-size: 12px; background: {color}; color: white; padding: 2px 10px; border-radius: 10px; display: inline-block;">目前位階</div>
                                </div>
                                <div style="border-left: 1px solid #eee; height: 40px;"></div>
                                <div>
                                    <div style="font-size: 28px; font-weight: bold; color: #444;">{ma60:.2f}</div>
                                    <div style="font-size: 12px; color: #888;">季線 (60MA)</div>
                                </div>
                            </div>
                        </div>

                        <div style="background: #fff5f5; border-left: 5px solid #ff6b6b; padding: 15px; margin: 0 20px 20px 20px; border-radius: 8px;">
                            <div style="font-weight: bold; color: #ff6b6b; margin-bottom: 5px;">🐰 兔兔戰術建議：</div>
                            <div style="font-size: 14px; color: #444; line-height: 1.5;">{strategy}</div>
                        </div>

                        <div style="background: #f0f7ff; border-left: 5px solid #228be6; padding: 15px; margin: 0 20px 20px 20px; border-radius: 8px;">
                            <div style="font-weight: bold; color: #228be6; margin-bottom: 5px;">🤖 AI 智慧分析：</div>
                            <div style="font-size: 14px; color: #444; line-height: 1.5;">{ai_note}</div>
                        </div>

                        <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #555;">
                            <tr style="background: #fafafa; border-top: 1px solid #eee;">
                                <td style="padding: 12px 20px;">法人原始成本</td>
                                <td style="padding: 12px 20px; text-align: right; font-weight: bold;">{cost:.2f}</td>
                            </tr>
                            <tr style="background: #fff9db;">
                                <td style="padding: 12px 20px; color: #e67e22; font-weight: bold;">突破點 (1.04)</td>
                                <td style="padding: 12px 20px; text-align: right; font-weight: bold; color: #e67e22;">{p104:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 20px;">關卡一 (1.2高點)</td>
                                <td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t1:.2f}</td>
                            </tr>
                            <tr style="background: #fafafa;">
                                <td style="padding: 12px 20px;">關卡二 (1.4高點)</td>
                                <td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t2:.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 12px 20px;">關卡三 (1.7神獸點)</td>
                                <td style="padding: 12px 20px; text-align: right; font-weight: bold;">{t3:.2f}</td>
                            </tr>
                        </table>

                        <div style="padding: 15px; background: #ebfbee; color: #2b8a3e; font-size: 12px; line-height: 1.6; text-align: center;">
                            <b>🐰 兔子理財選股：</b>強勢股 | 法人加碼 | 多頭線型 | 成本區附近
                        </div>
                    </div>
                </div>
                '''
                components.html(full_card, height=750, scrolling=True)
            else:
                st.error("❌ 無法獲取數據，請確認代號正確。")
    except Exception as e:
        st.error(f"⚠️ 錯誤: {e}")
