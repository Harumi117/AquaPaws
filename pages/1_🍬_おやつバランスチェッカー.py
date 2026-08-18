import streamlit as st

st.set_page_config(page_title="おやつバランスチェッカー", page_icon="🍬")

FOOD_PRESETS = {
    "ドライ（平均3.6 kcal/g）": 3.6,
    "セミモイスト（平均3.0 kcal/g）": 3.0,
    "ウェット（平均1.0 kcal/g）": 1.0,
    "カスタム": None,
}

TREAT_PRESETS = {
    "ボーロ": 3.8,
    "チーズキューブ": 4.5,
    "干しさつまいも": 3.2,
    "ジャーキー": 3.5,
    "フリーズドライ肉": 5.6,
    "ヨーグルトドロップ": 5.4,
    "魚系ふりかけ": 3.5,
    "カスタム": None,
}

st.title("おやつバランスチェッカー 🍬")
st.caption("「今日のおやつ、どれくらい？」がパッと分かる。おやつのカロリー割合を計算してコメントします。")

if "treat_rows" not in st.session_state:
    st.session_state.treat_rows = [0]
    st.session_state.next_row_id = 1
    st.session_state.treat_type_0 = "ボーロ"
    st.session_state.treat_g_0 = 0.0
    st.session_state.treat_kcal_0 = TREAT_PRESETS["ボーロ"]


def sync_food_kcal():
    preset = FOOD_PRESETS[st.session_state.food_type]
    if preset is not None:
        st.session_state.food_kcal = preset


def sync_treat_kcal(rid):
    preset = TREAT_PRESETS[st.session_state[f"treat_type_{rid}"]]
    if preset is not None:
        st.session_state[f"treat_kcal_{rid}"] = preset


def add_row():
    rid = st.session_state.next_row_id
    st.session_state.next_row_id += 1
    st.session_state.treat_rows.append(rid)
    st.session_state[f"treat_type_{rid}"] = "ボーロ"
    st.session_state[f"treat_g_{rid}"] = 0.0
    st.session_state[f"treat_kcal_{rid}"] = TREAT_PRESETS["ボーロ"]


def remove_row(rid):
    st.session_state.treat_rows.remove(rid)
    for prefix in ("treat_type_", "treat_g_", "treat_kcal_"):
        st.session_state.pop(f"{prefix}{rid}", None)


col1, col2 = st.columns(2)

with col1:
    st.subheader("フード情報")

    weight = st.number_input(
        "体重（kg・任意）", min_value=0.0, step=0.1, value=0.0, format="%.1f",
        help="目安コメント表示に使います。未入力でもOKです。",
    )

    if "food_type" not in st.session_state:
        st.session_state.food_type = list(FOOD_PRESETS.keys())[0]
    if "food_kcal" not in st.session_state:
        st.session_state.food_kcal = FOOD_PRESETS[st.session_state.food_type]

    st.selectbox("フードの種類", list(FOOD_PRESETS.keys()), key="food_type", on_change=sync_food_kcal)
    food_kcal = st.number_input(
        "フードのカロリー密度（kcal/g）", min_value=0.0, step=0.1, key="food_kcal",
        help="種類選択で自動入力。必要なら上書きOK。",
    )
    food_g = st.number_input("1日のフード量（g）※必須", min_value=0.0, step=1.0, value=0.0)

st.subheader("おやつ（複数可）")
st.caption("代表的なおやつはカロリー密度をプリセット。商品により差があります。")

hcols = st.columns([3, 2, 2, 2, 1])
for h, label in zip(hcols, ["種類", "量（g）", "kcal/g", "小計（kcal）", ""]):
    h.markdown(f"**{label}**")

treat_kcal_total = 0.0
for rid in list(st.session_state.treat_rows):
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
    c1.selectbox(
        "種類", list(TREAT_PRESETS.keys()), key=f"treat_type_{rid}",
        label_visibility="collapsed", on_change=sync_treat_kcal, args=(rid,),
    )
    c2.number_input("量g", min_value=0.0, step=1.0, key=f"treat_g_{rid}", label_visibility="collapsed")
    c3.number_input("kcal/g", min_value=0.0, step=0.1, key=f"treat_kcal_{rid}", label_visibility="collapsed")

    g = st.session_state[f"treat_g_{rid}"]
    kcal_g = st.session_state[f"treat_kcal_{rid}"]
    subtotal = g * kcal_g
    treat_kcal_total += subtotal
    c4.write(f"{subtotal:.0f}")
    c5.button("✕", key=f"remove_{rid}", on_click=remove_row, args=(rid,))

st.button("＋ 行を追加", on_click=add_row)

food_kcal_total = food_g * food_kcal
total_kcal = food_kcal_total + treat_kcal_total
ratio = (treat_kcal_total / total_kcal * 100) if total_kcal > 0 else 0.0

with col2:
    st.subheader("結果")
    if food_g <= 0:
        st.info("フード量（g）とおやつを入れると計算します")
    elif treat_kcal_total <= 0:
        st.metric("おやつ比率", "— %")
        st.caption("おやつを入力すると計算します")
    else:
        st.metric("おやつ比率", f"{ratio:.1f} %")
        if ratio <= 10:
            st.success("適量の範囲内です👍")
        elif ratio <= 20:
            st.warning("やや多め。次のごはんで少し調整しましょう")
        else:
            st.error("おやつが多すぎるかも。見直しましょう")

    st.write(f"食事カロリー：{food_kcal_total:.0f} kcal")
    st.write(f"おやつカロリー合計：{treat_kcal_total:.0f} kcal")
    st.write(f"総カロリー（食事＋おやつ）：{total_kcal:.0f} kcal")

    if weight > 0:
        rer = 70 * (weight ** 0.75)
        st.caption(f"参考：体重{weight:.1f}kgの安静時エネルギー要求量(RER)は約{rer:.0f} kcalです。")

st.divider()
st.markdown(
    "※ この結果はあくまで一般的な目安です。体調・運動量・季節・去勢避妊の有無・年齢で必要量は変わります。  \n"
    "※ **持病や治療中の子は獣医師の指示を優先**してください。  \n\n"
    "参考プリセット：ドライ3.6、セミモイスト3.0、ウェット1.0（kcal/g）／"
    "ボーロ3.8／チーズキューブ4.5／干しさつまいも3.2／ジャーキー3.5／"
    "フリーズドライ肉5.6／ヨーグルトドロップ5.4／魚系ふりかけ3.5"
)
