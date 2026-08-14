import streamlit as st
import google.generativeai as genai

# --- ページ基本設定 ---
st.set_page_config(
    page_title="ダイエット＆トレーニングアプリ",
    page_icon="🏋️",
    layout="centered"
)

# --- SecretsからAPIキーを取得 ---
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        model = None
else:
    model = None

# --- サイドバー（ページ切り替え＆再読み込み） ---
st.sidebar.title("メニュー")
page = st.sidebar.radio("機能を選択", ["⚖️ 体重トラッカー", "🏋️ ジェミ相談室"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 再読み込み（アプリ更新）"):
    st.toast("画面を更新しました！")
    st.rerun()

# ==========================================
# ページ1：⚖️ 体重トラッカー
# ==========================================
if page == "⚖️ 体重トラッカー":
    st.title("⚖️ 体重トラッカー")
    st.write("毎日の体重を記録して、7日間平均で確実に成果をチェック！")
    
    st.markdown("---")
    st.header("☀️ 今朝の体重を入力")
    
    with st.expander("⚙️ トレーニング開始日の設定"):
        st.info("トレーニング開始日を設定して進捗を管理しましょう！")
    
    st.success("⏱️ トレーニング開始から: 1 日目")

# ==========================================
# ページ2：🏋️ ジェミ相談室
# ==========================================
elif page == "🏋️ ジェミ相談室":
    st.title("🏋️ ジェミ相談室")
    st.write("パーソナルトレーナー・ジェミになんでも相談できます！")
    
    st.info("「マシンの使い方」「食事メニュー」「トレーニングの提案」など、何でも相談してください！")
    
    # 会話履歴の保持
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("質問・相談を入力（例：どんなトレーニングがいい？）"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if not api_key or not model:
                st.error("⚠️ Secretsに GEMINI_API_KEY が正しく設定されていないか、キーが無効です。")
            else:
                with st.spinner("ジェミが考え中..."):
                    try:
                        system_instruction = "あなたは親切で励ましてくれる優秀なパーソナルトレーナー『ジェミ』です。"
                        full_prompt = f"{system_instruction}\nユーザーからの質問: {prompt}"
                        
                        response = model.generate_content(full_prompt)
                        if response and response.text:
                            reply_text = response.text
                            st.markdown(reply_text)
                            st.session_state.messages.append({"role": "assistant", "content": reply_text})
                        else:
                            st.error("応答を受け取れませんでした。")
                    except Exception as e:
                        st.error("現在AIとの通信でエラーが発生しています。少し時間をおいて再度お試しいただくか、APIキーをご確認ください。")
