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
# TAB 2: 今日のパーソナルメニュー（ジムの日のみ有酸素）
# ==========================================
with tab2:
    # 曜日ごとのメニュー定義（ジム週3回：月・水・金）
    WEEKLY_SCHEDULE = {
        0: { # 月曜日
            "day_name": "月曜日",
            "type": "🏋️‍♂️ 【ジムの日】上半身（胸・肩・二の腕）＋ 脂肪燃焼有酸素",
            "menu": [
                "1. チェストプレス（胸）: 10回 × 3セット",
                "2. ショルダープレス（肩）: 12回 × 3セット",
                "3. ケーブルトライセプスダウン（二の腕裏）: 15回 × 3セット",
                "4. クランチ（腹筋）: 15回 × 3セット",
                "🔥 【有酸素】トレッドミル（傾斜4〜6%、速度5〜6km/hで20〜30分早歩き）"
            ],
            "point": "大きな胸の筋肉を効かせた後、トレッドミルの『傾斜早歩き』で一気に脂肪を燃やします！"
        },
        1: { # 火曜日
            "day_name": "火曜日",
            "type": "🧘‍♂️ 完全オフ（筋肉の回復Day）",
            "menu": [
                "1. しっかり睡眠をとる",
                "2. タンパク質中心の食事を意識する",
                "3. 軽くお風呂でストレッチ"
            ],
            "point": "ジムはお休みです！しっかり休むことで筋肉が成長し、基礎代謝が上がります。"
        },
        2: { # 水曜日
            "day_name": "水曜日",
            "type": "🏋️‍♂️ 【ジムの日】下半身・腹筋 ＋ 脂肪燃焼有酸素",
            "menu": [
                "1. レッグプレス（脚全体）: 10回 × 3セット",
                "2. レッグカール（太もも裏）: 12回 × 3セット",
                "3. アブドミナル（腹筋マシン）: 15回 × 3セット",
                "🔥 【有酸素】エアロバイク（ペダル重め、心拍数120前後で20〜30分）"
            ],
            "point": "下半身の大きな筋肉を使った後はバイクで脂肪燃焼！足腰をしっかり強化します。"
        },
        3: { # 木曜日
            "day_name": "木曜日",
            "type": "🧘‍♂️ 完全オフ（リカバリーDay）",
            "menu": [
                "1. お風呂に浸かって血行促進",
                "2. 水分をしっかり摂る"
            ],
            "point": "筋肉の疲労を抜く大切な日です。しっかりリフレッシュしましょう！"
        },
        4: { # 金曜日
            "day_name": "金曜日",
            "type": "🏋️‍♂️ 【ジムの日】背中・腕 ＋ 脂肪燃焼有酸素",
            "menu": [
                "1. ラットプルダウン（背中）: 10回 × 3セット",
                "2. シーテッドローイング（背中中央）: 12回 × 3セット",
                "3. アームカール（力こぶ）: 12回 × 3セット",
                "🔥 【有酸素】トレッドミル または エアロバイク（20〜30分）"
            ],
            "point": "背中をしっかり鍛えて姿勢を整え、仕上げの有酸素で1週間の脂肪を燃やし切ります！"
        },
        5: { # 土曜日
            "day_name": "土曜日",
            "type": "🧘‍♂️ 休日リフレッシュDay",
            "menu": [
                "1. 好きな運動や趣味で体を軽くほぐす",
                "2. 栄養バランスの良い食事"
            ],
            "point": "ジムもお休み！土日は無理せず体を休めて、週明けのジムに備えましょう。"
        },
        6: { # 日曜日
            "day_name": "日曜日",
            "type": "🧘‍♂️ 休日リフレッシュDay",
            "menu": [
                "1. 全身の軽いストレッチ",
                "2. 7時間以上の十分な睡眠"
            ],
            "point": "1週間お疲れ様でした！明日からの月曜ジムに向けてしっかり充電してください。"
        }
    }

    # 今日の曜日を取得
    today_weekday = datetime.datetime.now().weekday()
    today_data = WEEKLY_SCHEDULE[today_weekday]

    st.header(f"📅 今日（{today_data['day_name']}）のメニュー")
    st.subheader(today_data["type"])
    
    st.markdown("---")
    for item in today_data["menu"]:
        st.write(f"- {item}")
    st.markdown("---")
    
    st.info(f"💡 **ジェミ・トレーナーのアドバイス:**\n\n{today_data['point']}")

    st.markdown("### 🗓️ 1週間の全体スケジュール")
    with st.expander("タップして全日程（月〜日）を見る"):
        for w, data in WEEKLY_SCHEDULE.items():
            st.markdown(f"**【{data['day_name']}】 {data['type']}**")

# ==========================================
# TAB 3: ジェミ相談室
# ==========================================
with tab3:
    st.header("🤖 パーソナルトレーナー・ジェミ")
    st.write("「今日の有酸素を長めにしたい」「マシンが混んでいる」など、何でも相談してください！")
    
    user_query = st.text_area("質問・相談を入力", placeholder="例：今日はジムのトレッドミルが混んでいたので、代わりにできるメニューを教えて！")
    
    if st.button("ジェミに相談する 💬", use_container_width=True):
        if user_query and api_key:
            model = genai.GenerativeModel("gemini-1.5-flash")
            system_prompt = (
                "あなたは熱心で知識豊富なプロのパーソナルトレーナー『ジェミ』です。"
                "ユーザーは80kgから70kgを目指してダイエット中です。"
                "科学的根拠に基づき、親切かつモチベーションが上がる回答をしてください。"
            )
            full_prompt = f"{system_prompt}\n\nユーザーの相談: {user_query}"
            
            with st.spinner("ジェミがメニューを考えています..."):
                try:
                    response = model.generate_content(full_prompt)
                    st.success("💪 ジェミからの回答:")
                    st.write(response.text)
                except Exception as e:
                    st.error("エラーが発生しました。時間を置いて再度お試しください。")
        elif not user_query:
            st.warning("相談内容を入力してください。")
