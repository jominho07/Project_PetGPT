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
# CSV 데이터 로드
# =========================

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "breeds.csv"
)

df = pd.read_csv(DATA_PATH)

# boolean 변환
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
        "본인의 하루 활동량 (산책 가능 수준)",
        options=["매우 적음", "보통", "활동적", "매우 활동적"]
    )

    has_allergy = st.checkbox("가족 중 털 알러지가 있는 분이 있나요?")

# =========================
# 점수 계산 함수
# =========================

def score(row):
    s = 0

    # 동물 타입
    if pet_type == "상관없음":
        s += 3
    elif row["type"] == pet_type:
        s += 3

    # 활동량 매칭
    if row["energy"] == activity_level:
        s += 3

    # 주거 환경
    if living_env == "아파트/빌라":
        if row["size"] == "소형":
            s += 2

    elif living_env == "단독주택":
        if row["size"] in ["소형", "중형"]:
            s += 2

    elif living_env == "마당 있는 집":
        if row["size"] in ["중형", "대형"]:
            s += 2

    # 알러지
    if has_allergy:
        if row["allergy_friendly"]:
            s += 3
        else:
            s -= 3

    return s

# =========================
# 추천 실행
# =========================

if st.button("추천 리스트 보기", type="primary"):

    result = df.copy()

    result["score"] = result.apply(score, axis=1)

    result = result.sort_values("score", ascending=False)

    top3 = result.head(3)

    st.success("당신에게 가장 잘 맞는 반려동물 TOP 3")

    cols = st.columns(len(top3))

    for col, (_, row) in zip(cols, top3.iterrows()):

        with col:
            with st.container(border=True):

                st.markdown(f"### 🐾 {row['breed']}")

                st.write(f"**{row['type']} · {row['size']}**")
                st.write(f"활동량: {row['energy']}")
                st.write(f"평균 수명: {row['life_span']}")

                if row["allergy_friendly"]:
                    st.success("알러지 친화 품종")

                st.progress(min(row["score"] / 10, 1.0))
                st.caption(f"적합도 점수: {row['score']}점")
