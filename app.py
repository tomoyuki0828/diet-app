import calendar
from datetime import datetime
import pandas as pd
import streamlit as st

# (例) df に '日付' (YYYY-MM-DD) と '体重' のデータが入っているとします
# 日付列を datetime 型に変換
df['日付'] = pd.to_datetime(df['日付'])

# --- 🗓️ 月選択のUIを追加 ---
st.subheader('📅 表示する月を選択')

# データ内にある「年・月」のリストを作成（例: ["2026-08", "2026-07"]）
df['年月'] = df['日付'].dt.strftime('%Y-%m')
available_months = sorted(df['年月'].unique(), reverse=True)

# 今月をデフォルトで選択（データがなければリストの先頭）
current_month_str = datetime.now().strftime('%Y-%m')
default_index = (
    available_months.index(current_month_str)
    if current_month_str in available_months
    else 0
)

# ドロップダウンで月を選べるようにする
selected_month = st.selectbox(
    '表示する年月を選んでください',
    options=available_months,
    index=default_index,
)

# --- 📊 選択された月の 1日〜月末 までのデータを抽出 ---
year, month = map(int, selected_month.split('-'))
_, last_day = calendar.monthrange(year, month)

# 1日〜月末の日付範囲を作成
start_date = pd.Timestamp(year, month, 1)
end_date = pd.Timestamp(year, month, last_day)

# 該当する月だけにデータを絞り込む
filtered_df = df[(df['日付'] >= start_date) & (df['日付'] <= end_date)]

# --- 📈 グラフ描画 ---
st.line_chart(filtered_df.set_index('日付')['体重'])
