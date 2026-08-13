import datetime
import os
import sqlite3
import google.generativeai as genai
import pandas as pd
import streamlit as st

# ====================================================
# 1. データベース初期化 (SQLite)
# ====================================================
DB_FILE = "fitness_master.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 体重ログ用
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_weights (
            date TEXT PRIMARY KEY,
            weight REAL
        )
    """
    )
    # トレーニングログ用
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            exercise TEXT,
            weight REAL,
            reps INTEGER,
            sets INTEGER
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# 前回トレーニング記録の取得関数
def get_last_workout(exercise_name):
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT weight, reps FROM workout_logs 
        WHERE exercise = ? 
        ORDER BY date DESC, id DESC LIMIT 1
    """
    df = pd.read_sql_query(query, conn, params=(exercise_name,))
    conn.close()
    if not df.empty:
        return df.iloc[0]["weight"], df.iloc[0]["reps"]
    return None, None


# ====================================================
# 2. アプリ画面設定 ＆ タブ構成
# ====================================================
st.set_page_config(
    page_title="ジェミと目指す！健康ダイエットApp",
    page_icon="🏋️‍♂️",
    layout="centered",
)

st.title("🏋️‍♂️ 健康ダイエット App")
st.caption("目標: 80kg → 70kg (週3ジム × 7日平均体重管理)")

GOAL_WEIGHT = 70.0
today_str = datetime.date.today().strftime("%Y-%m-%d")

tab1, tab2, tab3 = st.tabs(
    ["⚖️ 体重トラッカー", "💪 今日のジムトレ", "🤖 ジェミに相談"]
)

# ====================================================
# TAB 1: 毎朝10秒 体重トラッカー ＆ 7日平均管理
# ====================================================
with tab1:
    st.markdown("### ☀️ 今朝の体重を入力")

    conn = sqlite3.connect(DB_FILE)
    last_entry = pd.read_sql_query(
        "SELECT weight FROM daily_weights ORDER BY date DESC LIMIT 1", conn
    )
    conn.close()

    default_val = (
        float(last_entry.iloc[0]["weight"]) if not last_entry.empty else 80.0
    )

    with st.form("quick_weight_form"):
        col_in, col_btn = st.columns([3, 2])
        with col_in:
            input_weight = st.number_input(
                "体重 (kg)",
                min_value=40.0,
                max_value=150.0,
                value=default_val,
                step=0.1,
                format="%.1f",
                label_visibility="collapsed",
            )
        with col_btn:
            submit_weight = st.form_submit_button(
                "保存して分析 🚀", use_container_width=True
            )

        if submit_weight:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO daily_weights (date, weight) VALUES (?, ?)",
                (today_str, input_weight),
            )
            conn.commit()
            conn.close()
            st.toast(f"✅ {input_weight:.1f}kg を保存しました！", icon="🎉")
            st.rerun()

    st.divider()

    # 体重データの取得と自動分析
    conn = sqlite3.connect(DB_FILE)
    df_weight = pd.read_sql_query(
        "SELECT date, weight FROM daily_weights ORDER BY date ASC", conn
    )
    conn.close()

    if not df_weight.empty:
        df_weight["date"] = pd.to_datetime(df_weight["date"])
        df_weight = df_weight.sort_values("date").reset_index(drop=True)

        current_weight = df_weight["weight"].iloc[-1]
        prev_weight = (
            df_weight["weight"].iloc[-2]
            if len(df_weight) >= 2
            else current_weight
        )
        diff = current_weight - prev_weight

        # 7日移動平均
        df_weight["7d_avg"] = (
            df_weight["weight"].rolling(window=7, min_periods=1).mean()
        )
        current_7d_avg = df_weight["7d_avg"].iloc[-1]
        remaining_kg = current_weight - GOAL_WEIGHT

        # 70kg到達予測ロジック
        est_date_str = "データ蓄積中..."
        if len(df_weight) >= 3:
            sample_df = df_weight.tail(14)
            days_passed = (
                sample_df["date"].iloc[-1] - sample_df["date"].iloc[0]
            ).days
            weight_change = (
                sample_df["weight"].iloc[-1] - sample_df["weight"].iloc[0]
            )

            if days_passed > 0 and weight_change < 0:
                daily_rate = abs(weight_change) / days_passed
                days_needed = (
                    remaining_kg / daily_rate if daily_rate > 0 else 0
                )
                est_date = datetime.date.today() + datetime.timedelta(
                    days=int(days_needed)
                )
                est_date_str = f"{est_date.strftime('%Y年%m月%d日')} （あと約 {int(days_needed)} 日）"
            elif remaining_kg <= 0:
                est_date_str = "🎯 すでに目標達成済みです！"
            else:
                est_date_str = "減量ペースを測定中"

        # 分析指標の表示
        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                label="📉 7日平均体重",
                value=f"{current_7d_avg:.2f} kg",
                delta=f"{diff:+.1f} kg (前日比)",
            )
        with m2:
            st.metric(
                label="🎯 目標まであと",
                value=f"{remaining_kg:.1f} kg",
                delta=f"目標 {GOAL_WEIGHT:.1f} kg",
                delta_color="normal" if remaining_kg > 0 else "inverse",
            )

        st.success(f"📅 **70kg到達予測:** {est_date_str}")

        # グラフ描画
        st.markdown("### 📈 体重推移（7日平均ライン付）")
        chart_df = df_weight.set_index("date")[["weight", "7d_avg"]]
        chart_df.columns = ["日々の体重", "7日平均"]
        st.line_chart(chart_df)
    else:
        st.info("💡 上のフォームに体重を入力して記録を開始しましょう！")

# ====================================================
# TAB 2: ジムメニュー ＆ 重量ステップアップ管理
# ====================================================
with tab2:
    st.subheader("🔥 重量ステップアップナビ")

    exercises = [
        "レッグプレス（下半身）",
        "チェストプレス（胸）",
        "ラットプルダウン（背中）",
        "シーテッドロー（背中）",
        "ショルダープレス（肩）",
        "アブドミナル（腹筋）",
    ]
    selected_ex = st.selectbox("トレーニング種目を選択", exercises)

    last_weight, last_reps = get_last_workout(selected_ex)

    st.markdown("---")
    if last_weight is not None:
        st.write(f"**前回記録：** {last_weight} kg  ×  {last_reps} 回")

        # 重量自動提案ロジック (12回達成で+2.5kg)
        if last_reps >= 12:
            next_weight = last_weight + 2.5
            st.success(
                f"💪 **前回12回クリア！ 次回の目標： {next_weight} kg × 10〜12回** に挑戦！"
            )
        elif last_reps < 10:
            next_weight = last_weight
            st.warning(
                f"⚠️ **無理は禁物。次回も {next_weight} kg** できれいなフォームを意識！"
            )
        else:
            next_weight = last_weight
            st.info(
                f"👍 **次回も {next_weight} kg** でまずは12回達成を目指しましょう！"
            )
    else:
        st.info(
            "💡 この種目の過去記録はありません。本日の記録を入力してください。"
        )
        next_weight = 30.0

    st.markdown("---")

    with st.form("workout_input_form"):
        st.write(f"### 📝 結果を記録（{selected_ex}）")
        cw1, cw2, cw3 = st.columns(3)
        in_w = cw1.number_input(
            "今回重量(kg)", value=float(next_weight), step=2.5
        )
        in_r = cw2.number_input("こなせた回数", value=12, step=1)
        in_s = cw3.number_input("セット数", value=3, step=1)

        submit_workout = st.form_submit_button("トレーニング記録を保存")

        if submit_workout:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "INSERT INTO workout_logs (date, exercise, weight, reps, sets) VALUES (?, ?, ?, ?, ?)",
                (today_str, selected_ex, in_w, in_r, in_s),
            )
            conn.commit()
            conn.close()
            st.success(
                f"保存完了！ {selected_ex}: {in_w}kg × {in_r}回 を記録しました。"
            )
            st.rerun()

# ====================================================
# TAB 3: AI相棒 ジェミに相談（Gemini API）
# ====================================================
with tab3:
    st.subheader("💬 ジェミ（専属ダイエット相棒）")

    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

    if not api_key:
        st.warning(
            "⚠️ APIキー未設定です。StreamlitのSecrets機能に GEMINI_API_KEY を設定してください。"
        )
    else:
        genai.configure(api_key=api_key)

        system_instruction = """
        あなたは親しみやすく頼りになるAIトレ相棒「ジェミ」です。
        会話相手のプロフィール：
        - 年齢: 40歳（男性）/ 身長: 172cm / 開始時体重: 80kg / 目標: 70kg
        - 運動: 週3回ジム（1日おき、筋トレ→有酸素の順番）
        ジムのマシンの使い方、フォーム、食事（カロリー・PFC）、モチベーションを親身にサポートしてください。
        """

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
        )

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "model",
                    "content": "よっ！今日のジムの調子や食事の疑問、何でも聞いてね！相棒としてしっかりサポートするよ！💪",
                }
            ]

        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.write(msg["content"])

        if prompt := st.chat_input("ジェミに質問する（例：ジムの前にプロテイン飲んだ方がいい？）"):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("assistant"):
                with st.spinner("思考中..."):
                    try:
                        chat_history = [
                            {"role": m["role"], "parts": [m["content"]]}
                            for m in st.session_state.messages[:-1]
                        ]
                        chat = model.start_chat(history=chat_history)
                        response = chat.send_message(prompt)

                        st.write(response.text)
                        st.session_state.messages.append(
                            {"role": "model", "content": response.text}
                        )
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
