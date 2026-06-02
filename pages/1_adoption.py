import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth

auth.login_widget()

st.title("🏠 반려동물 추천 시스템")

# =========================
# CSV 로드
# =========================

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "breeds.csv"
)

df = pd.read_csv(DATA_PATH)

df["allergy_friendly"] = df["allergy_friendly"].astype(str).str.lower().eq("true")

# =========================
# 사용자 입력
# =========================

pet_type = st.selectbox("선호 동물", ["강아지", "고양이", "상관없음"])
activity = st.select_slider("활동량", ["매우 적음", "보통", "활동적", "매우 매우 활동적"])
allergy = st.checkbox("알러지 있음")

# =========================
# 점수 함수
# =========================

def score(row):
    s = 0

    if pet_type == "상관없음" or row["type"] == pet_type:
        s += 3

    if row["energy"] == activity:
        s += 3

    if allergy:
        s += 2 if row["allergy_friendly"] else -2

    return s


# =========================
# session state 초기화
# =========================

if "top3" not in st.session_state:
    st.session_state.top3 = None

if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None


# =========================
# 추천 버튼
# =========================

if st.button("추천 보기", type="primary"):

    temp = df.copy()
    temp["score"] = temp.apply(score, axis=1)

    st.session_state.top3 = temp.sort_values(
        "score",
        ascending=False
    ).head(3)

    st.session_state.selected_pet = None


# =========================
# TOP3 출력
# =========================

if st.session_state.top3 is not None:

    st.subheader("🏆 TOP 3 추천")

    cols = st.columns(len(st.session_state.top3))

    for col, (_, row) in zip(cols, st.session_state.top3.iterrows()):

        with col:
            with st.container(border=True):

                st.markdown(f"### 🐾 {row['breed']}")
                st.write(f"{row['type']} · {row['size']}")
                st.write(f"활동량: {row['energy']}")
                st.write(f"💰 {row['cost']}")

                # 클릭 버튼
                if st.button("상세 보기", key=row["breed"]):

                    st.session_state.selected_pet = row


# =========================
# 상세 정보 출력 (CSV 기반)
# =========================

if st.session_state.selected_pet is not None:

    pet = st.session_state.selected_pet

    st.divider()
    st.subheader(f"📌 {pet['breed']} 상세 정보")

    st.write(f"🏥 대표 질환: {pet['main_disease']}")
    st.write(f"💰 양육비: {pet['cost']}")

    if pet["allergy_friendly"]:
        st.success("알러지 친화 품종")

    st.caption("※ 모든 정보는 평균 기준이며 개체별 차이가 있습니다.")
