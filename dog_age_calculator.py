import streamlit as st

# アプリタイトル
st.title("犬の年齢計算アプリ 🐶")

# 入力フォーム
st.header("わんちゃんの情報を入力してください")
age = st.number_input("犬の年齢 (歳)", min_value=0.0, value=1.0, step=0.1)
size = st.selectbox(
    "犬のサイズ",
    ["小型犬（〜10kg）", "中型犬（10〜25kg）", "大型犬（25kg〜）"],
)

# 3歳以降、1年あたりに加算する人間年齢（サイズが大きいほど老化が早いとされる）
YEARS_PER_ADDITIONAL_YEAR = {
    "小型犬（〜10kg）": 4,
    "中型犬（10〜25kg）": 5,
    "大型犬（25kg〜）": 7,
}

# 計算ボタン
if st.button("人間年齢に換算する"):
    if age <= 1:
        human_age = age * 15
    elif age <= 2:
        human_age = 15 + (age - 1) * 9
    else:
        human_age = 24 + (age - 2) * YEARS_PER_ADDITIONAL_YEAR[size]

    # 結果表示
    st.subheader("計算結果")
    st.write(f"犬の年齢: {age:.1f} 歳")
    st.write(f"人間年齢に換算すると: 約 {human_age:.1f} 歳")

    if age < 1:
        stage = "子犬"
    elif age < 7:
        stage = "成犬"
    else:
        stage = "シニア犬"
    st.write(f"ライフステージの目安: {stage}")

# 補足情報
st.info("※ この計算は一般的な目安です。犬種や個体差により実際の成長速度は異なります。")
