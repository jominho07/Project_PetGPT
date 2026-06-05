import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth

auth.login_widget()

st.title("🏠 나에게 꼭 맞는 가족 찾기")
st.write("간단한 설문을 통해 운명의 반려동물을 추천해 드립니다.")

st.divider()

# =========================
# CSV 로드
# =========================

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "breeds.csv"
)

df = pd.read_csv(DATA_PATH)

df["allergy_friendly"] = (
    df["allergy_friendly"]
    .astype(str)
    .str.lower()
    .eq("true")
)

# =========================
# 사용자 입력
# =========================

col1, col2 = st.columns(2)

with col1:
    pet_type = st.selectbox(
        "선호하는 동물",
        ["강아지", "고양이", "상관없음"]
    )

    living_env = st.radio(
        "주거 환경",
        ["아파트/빌라", "단독주택", "마당 있는 집"]
    )

with col2:
    activity_level = st.select_slider(
        "활동량",
        options=["매우 적음", "보통", "활동적", "매우 활동적"]
    )

    has_allergy = st.checkbox("털 알러지가 있나요?")

# =========================
# 점수 함수
# =========================

def score(row):
    s = 0

    if pet_type == "상관없음":
        s += 3
    elif row["type"] == pet_type:
        s += 3

    if row["energy"] == activity_level:
        s += 3

    if living_env == "아파트/빌라":
        if row["size"] == "소형":
            s += 2

    elif living_env == "단독주택":
        if row["size"] in ["소형", "중형"]:
            s += 2

    elif living_env == "마당 있는 집":
        if row["size"] in ["중형", "대형"]:
            s += 2

    if has_allergy:
        if row["allergy_friendly"]:
            s += 3
        else:
            s -= 3

    return s

# =========================
# session state 초기화
# =========================

if "top3" not in st.session_state:
    st.session_state.top3 = None

if "selected" not in st.session_state:
    st.session_state.selected = None

# =========================
# 추천 실행
# =========================

if st.button("추천 리스트 보기", type="primary"):

    result = df.copy()
    result["score"] = result.apply(score, axis=1)

    if pet_type == "상관없음":

        dog_top3 = (
            result[result["type"] == "강아지"]
            .sort_values("score", ascending=False)
            .head(3)
        )

        cat_top3 = (
            result[result["type"] == "고양이"]
            .sort_values("score", ascending=False)
            .head(3)
        )

        st.session_state.top3 = pd.concat([dog_top3, cat_top3])

    else:

        st.session_state.top3 = result.sort_values(
            "score",
            ascending=False
        ).head(3)

    st.session_state.selected = None

# =========================
# TOP3 출력 (요약 버전)
# =========================

if st.session_state.top3 is not None:

    if pet_type == "상관없음":

        dog_top3 = st.session_state.top3[
            st.session_state.top3["type"] == "강아지"
        ]

        cat_top3 = st.session_state.top3[
            st.session_state.top3["type"] == "고양이"
        ]

        st.success("🏆 강아지 TOP 3")

        cols = st.columns(3)

        for col, (_, row) in zip(cols, dog_top3.iterrows()):

            with col:
                with st.container(border=True):

                    st.markdown(f"### 🐶 {row['breed']}")
                    st.write(f"📏 크기: {row['size']}")

                    if st.button(
                        "상세 보기",
                        key=f"dog_{row['breed']}"
                    ):
                        st.session_state.selected = row

        st.success("🏆 고양이 TOP 3")

        cols = st.columns(3)

        for col, (_, row) in zip(cols, cat_top3.iterrows()):

            with col:
                with st.container(border=True):

                    st.markdown(f"### 😺 {row['breed']}")
                    st.write(f"📏 크기: {row['size']}")

                    if st.button(
                        "상세 보기",
                        key=f"cat_{row['breed']}"
                    ):
                        st.session_state.selected = row

    else:

        st.success("🏆 추천 TOP 3")

        cols = st.columns(3)

        for col, (_, row) in zip(
            cols,
            st.session_state.top3.iterrows()
        ):

            with col:
                with st.container(border=True):

                    emoji = (
                        "🐶"
                        if row["type"] == "강아지"
                        else "😺"
                    )

                    st.markdown(f"### {emoji} {row['breed']}")
                    st.write(f"📏 크기: {row['size']}")

                    if st.button(
                        "상세 보기",
                        key=row["breed"]
                    ):
                        st.session_state.selected = row
# =========================
# 상세 정보 출력
# =========================

if st.session_state.selected is not None:

    pet = st.session_state.selected

    st.divider()
    st.subheader(f"📌 {pet['breed']} 상세 정보")

    st.write(f"🏥 대표 질환: {pet['main_disease']}")
    st.write(f"💰 양육비(월): {pet['cost']}")

    st.write(f"⚡ 활동량: {pet['energy']}")
    st.write(f"🧬 털 빠짐: {pet['shedding']}")


    if pet["allergy_friendly"]:
        st.success("알러지 친화 품종")

    if st.button("닫기"):
        st.session_state.selected = None
