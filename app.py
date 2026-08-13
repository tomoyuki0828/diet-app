import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="健康ダイエット App", page_icon="🏋️‍♂️", layout="centered")

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- タイトル ---
st.title("🏋️‍♂️ 健康ダイエット App")
st.caption("目標: 80kg → 70kg（週3ジムで【筋トレ ＋ 有酸素】効率ダイエット）")

# --- タブ作成 ---
tab1, tab2, tab3 = st.tabs(["⚖️ 体重トラッカー", "💪 今日のパーソナルメニュー", "🤖 ジェミ相談室"])

# ==========================================
# TAB 1: 体重トラッカー
# ==========================================
with tab1:
    st.header("☀️ 今朝の体重を入力")
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=80.0, step=0.1)
    
    if st.button("保存して分析 🚀", use_container_width=True):
        st.success(f"体重 {weight} kg を記録しました！")
        if api_key:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"現在の体重は {weight}kg（目標70kg）です。プロのパーソナルトレーナーとして、今日意識すべきモチベーションが上がるショートアドバイス（100文字程度）を1つ提供してください。"
            try:
                response = model.generate_content(prompt)
                st.info(f"💡 **ジェミのアドバイス:**\n\n{response.text}")
            except Exception as e:
                st.warning("AIメッセージの取得に失敗しました。")

# ==========================================
# TAB 2: 今日のパーソナルメニュー（回数・セット数強調表示）
# ==========================================
with tab2:
    # 曜日ごとの詳細メニュー定義
    WEEKLY_SCHEDULE = {
        0: { # 月曜日
            "day_name": "月曜日",
            "type": "🏋️‍♂️ 【ジムの日】上半身（胸・肩・二の腕）＋ 脂肪燃焼有酸素",
            "menu": [
                "1. **チェストプレス（胸・二の腕）**: **10回 × 3セット** （休憩 60〜90秒）\n   - 【マシン】胸を張って前に押す",
                "2. **ショルダープレス（肩）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】上に持ち上げる",
                "3. **ケーブルトライセプスダウン（二の腕裏）**: **15回 × 3セット** （休憩 60秒）\n   - 【ケーブルマシン】上から下に引く",
                "4. **クランチ（腹筋）**: **15回 × 3セット** （休憩 45秒）\n   - 【マット】お腹を丸める",
                "🔥 **【有酸素】トレッドミル（ランニングマシン）**: **20〜30分**\n   - 傾斜4〜6%、速度5〜6km/hの早歩き"
            ],
            "point": "大胸筋などの大きな筋肉をしっかり刺激した後に、トレッドミルの『傾斜早歩き』で脂肪を一気に燃やします！"
        },
        1: { # 火曜日
            "day_name": "火曜日",
            "type": "🧘‍♂️ 完全オフ（筋肉の回復Day）",
            "menu": [
                "1. **睡眠**: **7時間以上** しっかりとる",
                "2. **食事**: **タンパク質中心**（お肉・魚・プロテイン）を意識",
                "3. **ケア**: お風呂に浸かって軽くストレッチ"
            ],
            "point": "ジムはお休みです！筋肉を休ませることで基礎代謝が上がり、痩せやすい体になります。"
        },
        2: { # 水曜日
            "day_name": "水曜日",
            "type": "🏋️‍♂️ 【ジムの日】下半身・腹筋 ＋ 脂肪燃焼有酸素",
            "menu": [
                "1. **レッグプレス（太もも・お尻）**: **10回 × 3セット** （休憩 90秒）\n   - 【大型足押しマシン】両足でプレートを押す",
                "2. **レッグカール（太もも裏）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】うつ伏せまたは座って足を後ろに曲げる",
                "3. **アブドミナル（腹筋）**: **15回 × 3セット** （休憩 45秒）\n   - 【腹筋マシン】上半身を前に倒す",
                "🔥 **【有酸素】エアロバイク（固定式自転車）**: **20〜30分**\n   - ペダル重め、心拍数120前後をキープ"
            ],
            "point": "人体で最大の「下半身の筋肉」を使った後、バイクで有酸素運動！効率バツグンです。"
        },
        3: { # 木曜日
            "day_name": "木曜日",
            "type": "🧘‍♂️ 完全オフ（リカバリーDay）",
            "menu": [
                "1. **湯船**: お風呂にしっかり浸かる",
                "2. **水分**: こまめに水分補給する"
            ],
            "point": "疲労をしっかり抜く大切な日です。しっかりリフレッシュしましょう！"
        },
        4: { # 金曜日
            "day_name": "金曜日",
            "type": "🏋️‍♂️ 【ジムの日】背中・腕 ＋ 脂肪燃焼有酸素",
            "menu": [
                "1. **ラットプルダウン（背中）**: **10回 × 3セット** （休憩 60〜90秒）\n   - 【広背筋マシン】上からバーを胸に引き寄せる",
                "2. **シーテッドローイング（背中中央）**: **12回 × 3セット** （休憩 60秒）\n   - 【ローイングマシン】前からお腹にバーを引く",
                "3. **アームカール（力こぶ）**: **12回 × 3セット** （休憩 60秒）\n   - 【ダンベル/マシン】肘を曲げて持ち上げる",
                "🔥 **【有酸素】トレッドミル または エアロバイク**: **20〜30分**\n   - 脂肪燃焼ペース（会話ができるくらいの強度）"
            ],
            "point": "背中を鍛えると姿勢が整い、見た目も引き締まります！最後の有酸素で1週間の仕上げです。"
        },
        5: { # 土曜日
            "day_name": "土曜日",
            "type": "🧘‍♂️ 休日リフレッシュDay",
            "menu": [
                "1. 好きな運動や趣味で体を軽くほぐす",
                "2. 栄養バランスの良い食事"
            ],
            "point": "ジムもお休み！無理せず体を休めて、週明けのジムに備えましょう。"
        },
        6: { # 日曜日
            "day_name": "日曜日",
            "type": "🧘‍♂️ 休日リフレッシュDay",
            "menu": [
                "1. 全身の軽いストレッチ",
                "2. 十分な睡眠で体をリカバリー"
            ],
            "point": "1週間お疲れ様でした！明日からの月曜ジムに向けてエネルギーを充電してください。"
        }
    }

    # 今日の曜日を取得
    today_weekday = datetime.datetime.now().weekday()
    today_data = WEEKLY_SCHEDULE[today_weekday]

    st.header(f"📅 今日（{today_data['day_name']}）のメニュー")
    st.subheader(today_data["type"])
    
    st.markdown("---")
    for item in today_data["menu"]:
        st.markdown(f"- {item}")
    st.markdown("---")
    
    st.info(f"💡 **ジェミ・トレーナーのアドバイス:**\n\n{today_data['point']}")

    st.markdown("### 🗓️ 1週間の全体スケジュール（回数・セット数付き）")
    with st.expander("タップして全日程（月〜日）のメニューを見る"):
        for w, data in WEEKLY_SCHEDULE.items():
            st.markdown(f"#### 【{data['day_name']}】 {data['type']}")
            for item in data["menu"]:
                st.markdown(f"  * {item}")
            st.markdown("---")

# ==========================================
# TAB 3: ジェミ相談室
# ==========================================
with tab3:
    st.header("🤖 パーソナルトレーナー・ジェミ")
    st.write("「重さは何kgから始めればいい？」「インターバルはどれくらい？」など、何でも相談してください！")
    
    user_query = st.text_area("質問・相談を入力", placeholder="例：レッグプレスは何kgからスタートするのがおすすめ？")
    
    if st.button("ジェミに相談する 💬", use_container_width=True):
        if user_query and api_key:
            model = genai.GenerativeModel("gemini-1.5-flash")
            system_prompt = (
                "あなたは熱心で知識豊富なプロのパーソナルトレーナー『ジェミ』です。"
                "ユーザーは80kgから70kgを目指してダイエット中です。"
                "回数やセット数、適切な重量設定も含めて、科学的根拠に基づき親切かつモチベーションが上がる回答をしてください。"
            )
            full_prompt = f"{system_prompt}\n\nユーザーの相談: {user_query}"
            
            with st.spinner("ジェミがアドバイスを考え中..."):
                try:
                    response = model.generate_content(full_prompt)
                    st.success("💪 ジェミからの回答:")
                    st.write(response.text)
                except Exception as e:
                    st.error("エラーが発生しました。時間を置いて再度お試しください。")
        elif not user_query:
            st.warning("相談内容を入力してください。")
