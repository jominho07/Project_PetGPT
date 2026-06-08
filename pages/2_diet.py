import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
from db import upsert_pet

auth.login_widget()

st.title("🥗 건강한 맞춤 식단 매니저")
st.write("반려동물의 상태를 입력하면 하루 권장 칼로리와 맞춤 영양 가이드를 제공합니다.")

st.divider()

# =========================
# 기본 데이터
# =========================

NUTRIENT_GUIDE = {
    "관절/뼈": {
        "성분": "글루코사민, 콘드로이틴, 오메가3",
        "설명": "관절 움직임과 뼈 건강 관리에 도움을 줄 수 있어요."
    },
    "피부/모질": {
        "성분": "오메가3·6, 비오틴, 아연",
        "설명": "피부 장벽과 털 윤기 관리에 도움을 줄 수 있어요."
    },
    "체중 조절": {
        "성분": "L-카르니틴, 고단백·저지방, 식이섬유",
        "설명": "포만감 유지와 체중 관리에 도움을 줄 수 있어요."
    },
    "소화/장": {
        "성분": "프로바이오틱스, 프리바이오틱스, 식이섬유",
        "설명": "장 건강과 배변 상태 관리에 도움을 줄 수 있어요."
    },
    "눈물 자국": {
        "성분": "저알러지 단백질, 오메가3, 충분한 수분",
        "설명": "알러지 가능성과 수분 섭취를 함께 관리하는 것이 좋아요."
    },
}

DANGER_FOODS = {
    "강아지": [
        "초콜릿", "포도/건포도", "양파/마늘", "자일리톨",
        "알코올", "카페인", "아보카도", "닭뼈"
    ],
    "고양이": [
        "초콜릿", "양파/마늘", "알코올", "카페인",
        "날생선 과다 섭취", "우유", "포도/건포도", "강아지 사료"
    ]
}

FEED_DATA = [
    {
        "제품명": "라이트 케어 사료",
        "대상": "강아지",
        "추천 고민": "체중 조절",
        "kcal_per_100g": 320,
        "가격": 28000,
        "용량": "2kg",
        "특징": "저지방, 식이섬유 함유"
    },
    {
        "제품명": "스킨 앤 코트 사료",
        "대상": "강아지",
        "추천 고민": "피부/모질",
        "kcal_per_100g": 370,
        "가격": 35000,
        "용량": "2kg",
        "특징": "오메가3·6, 비오틴 함유"
    },
    {
        "제품명": "조인트 케어 사료",
        "대상": "강아지",
        "추천 고민": "관절/뼈",
        "kcal_per_100g": 360,
        "가격": 39000,
        "용량": "2kg",
        "특징": "글루코사민, 콘드로이틴 함유"
    },
    {
        "제품명": "캣 유리너리 케어",
        "대상": "고양이",
        "추천 고민": "소화/장",
        "kcal_per_100g": 350,
        "가격": 32000,
        "용량": "2kg",
        "특징": "수분 섭취 관리, 장 건강 도움"
    },
    {
        "제품명": "캣 헤어 앤 스킨",
        "대상": "고양이",
        "추천 고민": "피부/모질",
        "kcal_per_100g": 365,
        "가격": 36000,
        "용량": "2kg",
        "특징": "피부와 모질 관리용"
    },
    {
        "제품명": "캣 라이트 케어",
        "대상": "고양이",
        "추천 고민": "체중 조절",
        "kcal_per_100g": 310,
        "가격": 30000,
        "용량": "2kg",
        "특징": "저칼로리, 체중 관리용"
    },
]

feed_df = pd.DataFrame(FEED_DATA)
feed_df["100g당 가격"] = feed_df["가격"] / 20

# =========================
# 계산 함수
# =========================

def calc_calories(weight_kg, age, species, neutered, weight_control):
    rer = 70 * (weight_kg ** 0.75)

    if age < 1:
        factor = 2.5
    elif weight_control:
        factor = 1.0
    elif neutered:
        factor = 1.6 if species == "강아지" else 1.2
    else:
        factor = 1.8 if species == "강아지" else 1.4

    mer = rer * factor
    return rer, mer


def get_body_message(body_status):
    if body_status == "마른 편":
        return "현재 체중이 낮은 편이라 급격한 다이어트보다는 충분한 영양 섭취가 중요해요."
    elif body_status == "적정":
        return "현재 상태를 유지할 수 있도록 일정한 급여량과 활동량을 관리해 주세요."
    else:
        return "체중 관리가 필요할 수 있어요. 간식량과 하루 총 칼로리를 함께 줄이는 것이 좋아요."


def recommend_feeds(species, health_issues):
    if not health_issues:
        return feed_df[feed_df["대상"] == species]

    return feed_df[
        (feed_df["대상"] == species) &
        (feed_df["추천 고민"].isin(health_issues))
    ]

# =========================
# 세션 저장
# =========================

if "diet_results" not in st.session_state:
    st.session_state.diet_results = []

# =========================
# 입력 UI
# =========================

st.subheader("🐾 반려동물 프로필 등록")

with st.container(border=True):
    name = st.text_input("반려동물 이름", placeholder="예: 멍멍이")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("나이 (세)", min_value=0, max_value=30, step=1)
        species = st.radio("종류", ["강아지", "고양이"], horizontal=True)
        body_status = st.selectbox("체형 상태", ["마른 편", "적정", "통통한 편"])

    with col2:
        weight = st.number_input("몸무게 (kg)", min_value=0.0, step=0.1)
        neutered = st.checkbox("중성화 완료", value=True)
        activity = st.selectbox("활동량", ["낮음", "보통", "높음"])

    health_issues = st.multiselect(
        "특별히 신경 쓰고 싶은 건강 고민",
        ["관절/뼈", "피부/모질", "체중 조절", "소화/장", "눈물 자국"],
    )

# =========================
# 분석 실행
# =========================

if st.button("맞춤 식단 분석하기", type="primary"):

    if not name:
        st.warning("반려동물의 이름을 입력해 주세요.")

    elif weight <= 0:
        st.warning("몸무게를 입력해 주세요.")

    else:
        weight_control = "체중 조절" in health_issues or body_status == "통통한 편"

        rer, mer = calc_calories(
            weight,
            age,
            species,
            neutered,
            weight_control
        )

        if activity == "낮음":
            mer *= 0.9
        elif activity == "높음":
            mer *= 1.1

        grams = mer / 3500 * 1000

        result = {
            "이름": name,
            "종류": species,
            "나이": age,
            "몸무게": weight,
            "중성화": "완료" if neutered else "안 함",
            "체형": body_status,
            "활동량": activity,
            "하루 권장 칼로리": round(mer),
            "RER": round(rer),
            "권장 사료량(g)": round(grams),
            "건강 고민": ", ".join(health_issues) if health_issues else "없음"
        }

        st.session_state.diet_results.append(result)

        upsert_pet(
            name=name,
            species=species,
            age=age,
            weight=weight,
            neutered=neutered,
            mer=round(mer)
        )

        st.success(f"'{name}' 프로필이 저장되었어요.")

# =========================
# 결과 출력
# =========================

if st.session_state.diet_results:

    latest = st.session_state.diet_results[-1]

    st.divider()
    st.subheader(f"📊 {latest['이름']} 맞춤 영양 결과")

    m1, m2, m3 = st.columns(3)

    m1.metric("하루 권장 칼로리", f"{latest['하루 권장 칼로리']:,} kcal")
    m2.metric("RER", f"{latest['RER']:,} kcal")
    m3.metric("건사료 기준 급여량", f"{latest['권장 사료량(g)']} g")

    st.info(
        "일반 건사료 100g당 350kcal 기준으로 계산했어요. "
        "실제 급여량은 사료 포장지의 칼로리에 맞춰 조절해야 합니다."
    )

    st.write(get_body_message(latest["체형"]))

    # =========================
    # 건강 고민별 추천 영양 성분
    # =========================

    st.divider()
    st.subheader("🧬 건강 고민별 추천 영양 성분")

    if latest["건강 고민"] == "없음":
        st.write("특별한 건강 고민이 없다면 균형 잡힌 단백질, 지방, 비타민, 미네랄이 중요해요.")
    else:
        for issue in latest["건강 고민"].split(", "):
            guide = NUTRIENT_GUIDE[issue]

            with st.container(border=True):
                st.markdown(f"### {issue}")
                st.write(f"**추천 성분:** {guide['성분']}")
                st.write(guide["설명"])

    # =========================
    # 시중 사료 비교 검색
    # =========================

    st.divider()
    st.subheader("🔍 시중 사료 비교 검색")

    feed_result = recommend_feeds(
        latest["종류"],
        latest["건강 고민"].split(", ") if latest["건강 고민"] != "없음" else []
    )

    if feed_result.empty:
        st.warning("조건에 맞는 사료가 없어 기본 사료 목록을 보여드릴게요.")
        feed_result = feed_df[feed_df["대상"] == latest["종류"]]

    st.dataframe(
        feed_result = feed_result.copy()

feed_result["가격"] = feed_result["가격"].apply(
    lambda x: f"{x:,}원"
)

feed_result["100g당 가격"] = feed_result["100g당 가격"].apply(
    lambda x: f"{x:,.0f}원"
)

st.dataframe(
    feed_result[
        [
            "제품명",
            "대상",
            "추천 고민",
            "kcal_per_100g",
            "가격",
            "용량",
            "100g당 가격",
            "특징"
        ]
    ],
    use_container_width=True,
    hide_index=True
)
    )

    # =========================
    # 위험 음식 목록
    # =========================

    st.divider()
    st.subheader("⚠️ 반려동물 위험 음식 목록")

    danger_cols = st.columns(4)

    for col, food in zip(danger_cols * 3, DANGER_FOODS[latest["종류"]]):
        with col:
            st.error(food)

# =========================
# 다묘·다견 프로필 동시 관리
# =========================

if st.session_state.diet_results:

    st.divider()
    st.subheader("🐶🐱 다묘·다견 프로필 관리")

    result_df = pd.DataFrame(st.session_state.diet_results)

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    total_kcal = result_df["하루 권장 칼로리"].sum()
    total_gram = result_df["권장 사료량(g)"].sum()

    c1, c2 = st.columns(2)

    c1.metric("전체 하루 필요 칼로리", f"{total_kcal:,} kcal")
    c2.metric("전체 하루 예상 사료량", f"{total_gram:,} g")
