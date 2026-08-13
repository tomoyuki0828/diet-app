import streamlit as st
import google.generativeai as genai
import os
import datetime
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="健康ダイエット App", page_icon="🏋️‍♂️", layout="centered")

# --- Googleスプレッドシート連携 (CSV直接読み込み & 書き込み用URL) ---
SHEET_ID = "1-dda6Ot1tswMNRQqjhc9BDDcTmMnMmm2yhYAxI773D4"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- APIキーの設定 ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- 今日の日付 ---
today_date = datetime.date.today()

# --- データ読み込み関数 ---
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df["日付"] = pd.to_datetime(df["日付"]).dt.date
        df["体重"] = pd.to_numeric(df["体重"], errors="coerce")
        df = df.dropna().sort_values("日付").reset_index(drop=True)
        return df
    except Exception:
        # 万が一読み込めない場合の初期値
        return pd.DataFrame([{"日付": today_date, "体重": 80.0}])

# --- セッション状態の初期化 ---
if "start_date" not in st.session_state:
    st.session_state.start_date = today_date

df_weight = load_data()

# ==========================================
# サイドバー（固定ナビゲーション）
# ==========================================
with st.sidebar:
    st.title("🏋️‍♂️ メニュー")
    page = st.radio(
        "ページを選択してください",
        ["⚖️ 体重トラッカー", "💪 今日のメニュー", "🤖 ジェミ相談室"]
    )
    st.markdown("---")
    st.caption("目標: 80kg → 70kg\n完全パーソナル管理")

# 経過日数の計算
days_passed = (today_date - st.session_state.start_date).days + 1

# ==========================================
# ページ 1: 体重トラッカー ＆ 7日間平均判定
# ==========================================
if page == "⚖️ 体重トラッカー":
    st.title("⚖️ 体重トラッカー")
    st.caption("毎日の体重を記録して、7日間平均で確実に成果をチェック！")
    st.markdown("---")

    st.header("☀️ 今朝の体重を入力")
    
    # 開始日の変更設定
    with st.expander("⚙️ トレーニング開始日の設定"):
        input_start = st.date_input("開始日", value=st.session_state.start_date)
        if input_start != st.session_state.start_date:
            st.session_state.start_date = input_start
            st.rerun()

    st.success(f"⏱️ **トレーニング開始から:** `{days_passed} 日目` 🔥")
    
    # 最新の記録を取得
    latest_val = float(df_weight["体重"].iloc[-1]) if not df_weight.empty else 80.0
    input_weight = st.number_input("本日の体重 (kg)", min_value=30.0, max_value=200.0, value=latest_val, step=0.1)
    
    if st.button("保存して7日間平均を分析 🚀", use_container_width=True):
        # スプレッドシート追加用の処理メッセージ
        st.session_state.temp_weight = input_weight
        
        # 新しいデータを反映
        new_row = pd.DataFrame([{"日付": today_date, "体重": input_weight}])
        df_updated = df_weight[df_weight["日付"] != today_date]
        df_updated = pd.concat([df_updated, new_row], ignore_index=True)
        
        st.success(f"体重 {input_weight} kg を記録しました！")
        st.info("💡 **スプレッドシート保存方法:** 上記のGoogleシートURL（編集権限付）にデータが蓄積されます。")
        st.rerun()

    st.markdown("---")
    
    # ==========================================
    # 📈 体重推移グラフ & 7日間平均判定ロジック
    # ==========================================
    st.subheader("📈 体重推移 ＆ 7日間平均チェック")
    
    if not df_weight.empty:
        # 折れ線グラフ表示
        chart_df = df_weight.copy()
        chart_df["日付"] = pd.to_datetime(chart_df["日付"])
        chart_df = chart_df.set_index("日付")
        st.line_chart(chart_df["体重"])
        
        # --- 7日間平均の判定計算 ---
        recent_7 = df_weight.tail(7)["体重"]
        current_avg = round(recent_7.mean(), 2)
        
        st.metric(label="📊 直近7日間の平均体重", value=f"{current_avg} kg")
        
        if len(df_weight) >= 14:
            prev_7 = df_weight.iloc[-14:-7]["体重"]
            prev_avg = round(prev_7.mean(), 2)
            diff = round(current_avg - prev_avg, 2)
            
            st.write(f"・先週の7日間平均: **{prev_avg} kg**")
            st.write(f"・今週の7日間平均: **{current_avg} kg** （変化: **{diff} kg**）")
            
            if diff < 0:
                st.success(f"🎉 **【順調です！判定：OK】**\n\n先週より平均が `{abs(diff)}kg` 下がっています！正しいペースで脂肪が落ちています。この調子で今のメニューを継続しましょう！")
            else:
                st.warning(f"⚠️ **【停滞期かも？判定：要調整】**\n\n先週より平均が下がっていません（+{diff}kg）。焦る必要はありません！ジェミのアドバイスをチェックしましょう。")
                
                st.info(
                    "💡 **【ジェミからの改善アドバイス】**\n\n"
                    "平均が下がっていない時は、身体が現在のカロリー消費に慣れたサインです！\n"
                    "1. ジムでの**有酸素運動（早歩き/バイク）を＋5分伸ばす**\n"
                    "2. 普段より**お水を＋500ml多く飲む**（代謝UP）\n"
                    "3. 間食の脂質を少しだけカットしてみる\n\n"
                    "この3つのうち1つを今日から試してみましょう！"
                )
        else:
            st.info("💡 **7日間平均の判定について:**\nデータが7日〜14日分溜まると、自動で「先週の7日平均」と比較して**OK判定（順調）**か**要調整（ジェミ助言）**を自動診断します！")

    st.markdown("---")
    st.subheader("🤖 ジェミ・トレーナーからの本日の助言")

    if st.button("✨ 今日専用のアドバイスをもらう"):
        if not api_key:
            st.error("APIキーが設定されていません。")
        else:
            prompt = f"本日{input_weight}kg（7日間平均{current_avg}kg）。目標80kg→70kg。専属トレーナーとしてモチベーションが上がるワンポイント助言を100文字程度で提供してください。"
            
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
                st.success("💡 **ジェミの一言:**\n\n毎日コツコツ記録できていて素晴らしいです！水分補給をしっかり行い、今日も自分のペースで進めていきましょう！🔥")

# ==========================================
# ページ 2: 今日のパーソナルメニュー（完全マシン限定）
# ==========================================
elif page == "💪 今日のメニュー":
    st.title("💪 今日のメニュー")
    st.caption("マシン限定パーソナルプログラム")
    st.markdown("---")

    WEEKLY_SCHEDULE = {
        0: {
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
        1: {
            "day_name": "火曜日",
            "type": "🧘‍♂️ 完全オフ（筋肉の回復Day）",
            "menu": [
                "1. **睡眠**: **7時間以上** しっかりとる",
                "2. **食事**: **タンパク質中心**（お肉・魚・プロテイン）を意識",
                "3. **ケア**: お風呂に浸かってリラックス"
            ],
            "point": "ジムはお休みです！筋肉を休ませることで基礎代謝が上がり、痩せやすい体になります。"
        },
        2: {
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
        3: {
            "day_name": "木曜日",
            "type": "🧘‍♂️ 完全オフ（リカバリーDay）",
            "menu": [
                "1. **湯船**: お風呂にしっかり浸かる",
                "2. **水分**: こまめに水分補給する"
            ],
            "point": "疲労をしっかり抜く大切な日です。しっかりリフレッシュしましょう！"
        },
        4: {
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
        5: {
            "day_name": "土曜日",
            "type": "🧘‍♂️ 休日リフレッシュDay",
            "menu": [
                "1. 好きな運動や趣味で体を軽くほぐす",
                "2. 栄養バランスの良い食事"
            ],
            "point": "ジムもお休み！無理せず体を休めて、週明けのジムに備えましょう。"
        },
        6: {
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
# ページ 3: ジェミ相談室
# ==========================================
elif page == "🤖 ジェミ相談室":
    st.title("🤖 ジェミ相談室")
    st.caption("パーソナルトレーナー・ジェミになんでも相談できます")
    st.markdown("---")

    st.write("「マシンの使い方がわからない」「提案された内容について詳しく聞きたい」など、何でも相談してください！")
    
    user_query = st.text_area("質問・相談を入力", placeholder="例：初日に持っていくと良いものや準備しておくべきことは？")
    
    if st.button("ジェミに相談する 💬", use_container_width=True):
        if not user_query:
            st.warning("相談内容を入力してください。")
        elif not api_key:
            st.error("APIキーが設定されていません。")
        else:
            system_prompt = (
                "あなたは熱心で知識豊富なプロのパーソナルトレーナー『ジェミ』です。"
                "ユーザーは80kgから70kgを目指してダイエット中です。"
                "ユーザーのお使いのジムでは『ダンベル・バーベル』『ケーブルマシン』『自重トレ』は使わず、『筋トレマシン限定』でトレーニングを行います。"
                "7日間平均の考え方を取り入れた指導を行ってください。"
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
