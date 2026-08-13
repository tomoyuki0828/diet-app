import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="健康ダイエット App", page_icon="🏋️‍♂️", layout="centered")

# --- CSS設定（スマホでも確実にタブを上部固定） ---
st.markdown("""
    <style>
    /* モバイル・Web共通：タブ全体のリスト部分を画面上部に固定 */
    div[data-testid="stTabs"] > div:first-child {
        position: sticky;
        top: 0;
        background-color: #ffffff;
        z-index: 9999;
        padding-top: 8px;
        padding-bottom: 8px;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* タブ切り替え時のスクロール位置ズレを防止 */
    .stMainBlockContainer {
        padding-top: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- タイトル ---
st.title("🏋️‍♂️ 健康ダイエット App")
st.caption("目標: 80kg → 70kg（完全パーソナル管理 × 筋トレマシン限定プログラム）")

# --- 明日スタートの設定 ---
tomorrow = datetime.date.today() + datetime.timedelta(days=1)

# --- セッション状態の初期化（開始日・体重履歴） ---
if "start_date" not in st.session_state:
    st.session_state.start_date = tomorrow
if "weight_history" not in st.session_state:
    st.session_state.weight_history = {tomorrow: 80.0}

# --- タブ作成 ---
tab1, tab2, tab3 = st.tabs(["⚖️ 体重トラッカー", "💪 今日のパーソナルメニュー", "🤖 ジェミ相談室"])

# 今日の日付と経過日数
today_date = datetime.date.today()
days_passed = (today_date - st.session_state.start_date).days + 1

# 最新の体重変化を取得
weights = list(st.session_state.weight_history.values())
latest_weight = weights[-1]
initial_weight = weights[0]
weight_diff = round(latest_weight - initial_weight, 1)

# ==========================================
# TAB 1: 体重トラッカー ＆ ジェミの総合提案
# ==========================================
with tab1:
    st.header("☀️ 今朝の体重を入力")
    
    # 開始日の変更設定
    with st.expander("⚙️ トレーニング開始日の設定"):
        input_start = st.date_input("開始日", value=st.session_state.start_date)
        if input_start != st.session_state.start_date:
            st.session_state.start_date = input_start
            st.rerun()

    if days_passed <= 0:
        st.info(f"🚩 **トレーニング開始予定日:** `{st.session_state.start_date}`（いよいよ明日スタート！）")
    else:
        st.write(f"⏱️ **トレーニング開始から:** `{days_passed} 日目`")
    
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=float(latest_weight), step=0.1)
    
    if st.button("保存して分析 🚀", use_container_width=True):
        st.session_state.weight_history[today_date] = weight
        st.success(f"体重 {weight} kg を記録しました！")
        st.rerun()

    st.markdown("---")
    st.subheader("🤖 ジェミ・トレーナーからの定期診断＆提案")

    # 日数 ✕ 体重推移の総合判断ロジック
    if days_passed <= 0:
        advice_status = "🔥 **【明日からスタート！】**"
        proposal = (
            "いよいよ明日から『目標70kg』へ向けたトレーニングがスタートします！\n\n"
            "初日は焦らず、マシンのシートの高さや使い方の確認から始めていきましょう。明日の朝、体重を記録して準備完了です！"
        )
    elif days_passed < 7:
        advice_status = "🌱 **【準備・慣れ期間】**"
        proposal = (
            f"現在 {days_passed} 日目（変化: {weight_diff}kg）です！\n\n"
            "まずはマシンの使い方とフォームに慣れることが最優先。重さは『少し軽め』で10〜12回丁寧に動かすことを意識しましょう！"
        )
    elif 7 <= days_passed < 30:
        if weight_diff <= -1.0:
            advice_status = "🔥 **【順調なペース！】**"
            proposal = (
                f"開始 {days_passed} 日目で `-{-weight_diff}kg`！非常に良いペースで脂肪が燃えています！\n\n"
                "現在の「週3回マシン＋有酸素」が完璧に機能しています。このまま現在のメニューを継続していきましょう！"
            )
        else:
            advice_status = "💡 **【調整のご提案】**"
            proposal = (
                f"開始 {days_passed} 日目（変化: {weight_diff}kg）です。\n\n"
                "少し体重が落ちにくい時期かもしれません。もし余裕があれば、ジムでの有酸素運動（トレッドミル/バイク）の時間を **＋5分** 伸ばしてみませんか？"
            )
    elif days_passed >= 30:
        advice_status = "🎉 **【1ヶ月達成！プログラム更新のご提案】**"
        proposal = (
            f"祝・1ヶ月達成！現在の体重変化: `{weight_diff}kg` です！\n\n"
            "体が現在のマシンメニューの刺激に慣れてくる頃です。筋肉に新しい刺激を与えてさらに痩せやすくするために、**『第2章：新マシンプログラム』へのアップデート**をおすすめします！\n\n"
            "👉 チャットでジェミに『1ヶ月経ったから新しいメニューにして！』と声をかけてくださいね！"
        )

    st.info(f"{advice_status}\n\n{proposal}")

    if st.button("✨ ジェミから今日のワンポイント助言をもらう"):
        if not api_key:
            st.error("APIキーが設定されていません。StreamlitのSecrets設定をご確認ください。")
        else:
            prompt = f"明日からトレーニング開始予定（目標80kg→70kg）です。専属トレーナーとして、初日に向けたやる気が湧くアドバイスを100文字程度で提供してください。"
            
            models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            success = False
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    st.success(f"💡 **ジェミの一言:**\n\n{response.text}")
                    success = True
                    break
                except Exception:
                    continue
            
            if not success:
                st.success("💡 **ジェミの一言:**\n\n明日はいよいよ初日ですね！焦らずマシンの設定確認からスタートしましょう。水分補給と十分な睡眠をとって明日に備えてくださいね！🔥")

# ==========================================
# TAB 2: 今日のパーソナルメニュー（完全マシン限定）
# ==========================================
with tab2:
    WEEKLY_SCHEDULE = {
        0: { # 月曜日
            "day_name": "月曜日",
            "type": "🏋️‍♂️ 【ジムの日】上半身（胸・肩・二の腕）＋ 脂肪燃焼有酸素",
            "menu": [
                "1. **チェストプレス（胸・二の腕）**: **10回 × 3セット** （休憩 60〜90秒）\n   - 【マシン】胸を張ってグリップを前に押す",
                "2. **ショルダープレス（肩）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】グリップを上に持ち上げる",
                "3. **ディップスマシン（二の腕裏）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】シートに座り、両脇のグリップを下に押し下げる",
                "4. **アブドミナル（腹筋）**: **15回 × 3セット** （休憩 45秒）\n   - 【マシン】シートに座り、お腹の力で上半身を前に倒す",
                "🔥 **【有酸素】トレッドミル（ランニングマシン）**: **20〜30分**\n   - 傾斜4〜6%、速度5〜6km/hの早歩き"
            ],
            "point": "マシンに身体を固定して大きな筋肉を安全に追い込みます！筋トレ後の『傾斜早歩き』で脂肪を一気に燃やしましょう！"
        },
        1: { # 火曜日
            "day_name": "火曜日",
            "type": "🧘‍♂️ 完全オフ（筋肉の回復Day）",
            "menu": [
                "1. **睡眠**: **7時間以上** しっかりとる",
                "2. **食事**: **タンパク質中心**（お肉・魚・プロテイン）を意識",
                "3. **ケア**: お風呂に浸かってリラックス"
            ],
            "point": "ジムはお休みです！筋肉を休ませることで基礎代謝が上がり、痩せやすい体になります。"
        },
        2: { # 水曜日
            "day_name": "水曜日",
            "type": "🏋️‍♂️ 【ジムの日】下半身・腹筋 ＋ 脂肪燃焼有酸素",
            "menu": [
                "1. **レッグプレス（太もも・お尻）**: **10回 × 3セット** （休憩 90秒）\n   - 【大型足押しマシン】シートに座り、両足でプレートを押す",
                "2. **レッグカール（太もも裏）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】座って足を後ろに曲げる",
                "3. **トーソローテーション（くびれ・お腹）**: **15回 × 3セット** （休憩 45秒）\n   - 【回転マシン】シートに座り、上半身を左右にひねる",
                "🔥 **【有酸素】エアロバイク（固定式自転車）**: **20〜30分**\n   - ペダル重め、心拍数120前後をキープ"
            ],
            "point": "人体で最大の「下半身のマシン」を使った後、バイクで有酸素運動！効率バツグンです。"
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
                "2. **シーテッドローイング（背中中央）**: **12回 × 3セット** （休憩 60秒）\n   - 【ローイングマシン】前からお腹に向かってバーを引く",
                "3. **アームカールマシン（力こぶ）**: **12回 × 3セット** （休憩 60秒）\n   - 【マシン】肘をパッドに固定し、グリップを上に持ち上げる",
                "🔥 **【有酸素】トレッドミル または エアロバイク**: **20〜30分**\n   - 脂肪燃焼ペース（会話ができるくらいの強度）"
            ],
            "point": "背中マシンで姿勢を整え、見た目を引き締めます！最後の有酸素で1週間の仕上げです。"
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
                "1. お風呂でリフレッシュ",
                "2. 十分な睡眠で体をリカバリー"
            ],
            "point": "1週間お疲れ様でした！明日からの月曜ジムに向けてエネルギーを充電してください。"
        }
    }

    today_weekday = datetime.datetime.now().weekday()
    today_data = WEEKLY_SCHEDULE[today_weekday]

    st.header(f"📅 今日（{today_data['day_name']}）のメニュー")
    st.subheader(today_data["type"])
    
    st.markdown("---")
    for item in today_data["menu"]:
        st.markdown(f"- {item}")
    st.markdown("---")
    
    st.info(f"💡 **ジェミ・トレーナーのアドバイス:**\n\n{today_data['point']}")

    st.markdown("### 🗓️ 1週間の全体スケジュール（筋トレマシン限定）")
    with st.expander("タップして全日程（月〜日）のマシンメニューを見る"):
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
    st.write("「マシンの使い方がわからない」「提案された内容について詳しく聞きたい」など、何でも相談してください！")
    
    user_query = st.text_area("質問・相談を入力", placeholder="例：初日に持っていくと良いものや準備しておくべきことは？")
    
    if st.button("ジェミに相談する 💬", use_container_width=True):
        if not user_query:
            st.warning("相談内容を入力してください。")
        elif not api_key:
            st.error("APIキーが設定されていません。StreamlitのSecrets設定をご確認ください。")
        else:
            system_prompt = (
                "あなたは熱心で知識豊富なプロのパーソナルトレーナー『ジェミ』です。"
                "ユーザーは80kgから70kgを目指してダイエット中です。"
                "ユーザーのお使いのジムでは『ダンベル・バーベル』『ケーブルマシン』『自重トレ』は使わず、『筋トレマシン限定』でトレーニングを行います。"
                "体重や経過日数のアドバイスも含めて、親切かつモチベーションが上がる回答をしてください。"
            )
            full_prompt = f"{system_prompt}\n\nユーザーの相談: {user_query}"
            
            with st.spinner("ジェミがアドバイスを考え中..."):
                models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
                success = False
                
                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(full_prompt)
                        st.success("💪 ジェミからの回答:")
                        st.write(response.text)
                        success = True
                        break
                    except Exception:
                        continue
                
                if not success:
                    st.error("現在AIとの通信が混み合っています。少し時間をおいて再度お試しください。")
