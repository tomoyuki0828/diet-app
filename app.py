import streamlit as st
import google.generativeai as genai

# --- ページ基本設定 ---
st.set_page_config(
    page_title="パーソナルトレーナー・ジェミ",
    page_icon="🏋️",
    layout="centered"
)

# --- SecretsからAPIキーを安全に取得・設定 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ APIキーが設定されていません。Streamlit CloudのSecretsに『GEMINI_API_KEY』を設定してください。")
    st.stop()

try:
    genai.configure(api_key=api_key)
    # 軽量で安定したモデルを指定
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"APIの初期化でエラーが発生しました: {e}")
    st.stop()

# --- タイトル ---
st.title("🏋️ ジェミ相談室")
st.write("パーソナルトレーナー・ジェミになんでも相談できます！")

# --- セッション状態（会話履歴・再読み込み用）の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー：再読み込みボタン ---
with st.sidebar:
    st.header("⚙️ 設定・操作")
    if st.button("🔄 再読み込み（履歴クリア）"):
        st.session_state.messages = []
        st.rerun()

# --- 案内表示 ---
st.info("「マシンの使い方」「食事メニュー」「トレーニングの提案」など、何でも気軽にどうぞ！")

# --- 過去の会話履歴を表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- チャット入力欄 ---
if prompt := st.chat_input("質問・相談を入力（例：どんなトレーニングがいい？）"):
    # ユーザーのメッセージを表示＆保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIの返答を生成＆表示
    with st.chat_message("assistant"):
        with st.spinner("ジェミが考え中..."):
            try:
                # システムプロンプト風のコンテキストを含めて回答生成
                system_instruction = "あなたは親切で励ましてくれる優秀なパーソナルトレーナー『ジェミ』です。"
                full_prompt = f"{system_instruction}\nユーザーからの質問: {prompt}"
                
                response = model.generate_content(full_prompt)
                
                if response and response.text:
                    reply_text = response.text
                    st.markdown(reply_text)
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                else:
                    st.error("応答を取得できませんでした。")
            except Exception as e:
                st.error("現在AIとの通信でエラーが発生しています。SecretsのGEMINI_API_KEYが正しいか確認してください。")
