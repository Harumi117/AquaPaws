import streamlit as st
import math

# アプリタイトル
st.title("犬の1日必要水分量計算アプリ")

# 入力フォーム
st.header("わんちゃんの情報を入力してください")
weight = st.number_input("体重 (kg)", min_value=0.1, value=10.0, step=0.1)

# 計算ボタン
if st.button("水分量を計算する"):
    # RERの計算
    rer = 70 * (math.pow(weight, 0.75))
    water_requirement = rer  # 水分量はRERと同量
    
    # 結果表示
    st.subheader("計算結果")
    st.write(f"わんちゃんの体重: {weight:.1f} kg")
    st.write(f"1日に必要な水分量: 約 {water_requirement:.1f} ml")

# 補足情報
st.info("※ この計算は一般的な目安です。運動量や季節に応じて調整してください。")
