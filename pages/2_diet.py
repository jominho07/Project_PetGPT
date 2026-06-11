import streamlit as st
import pandas as pd
import sys, os
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
from db import upsert_pet, get_pets, delete_pet

auth.login_widget()

st.title("맞춤 식단 매니저")
st.write("품종 데이터와 반려동물 상태를 기반으로 하루 권장 칼로리와 맞춤 사료를 추천합니다.")

st.divider()

# =========================
# CSV 로드
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BREEDS_PATH = os.path.join(BASE_DIR, "data", "breeds.csv")

breed_df = pd.read_csv(BREEDS_PATH)

breed_df["allergy_friendly"] = (
    breed_df["allergy_friendly"]
    .astype(str)
    .str.lower()
    .eq("true")
)

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
    "요로/신장": {
        "성분": "충분한 수분, 마그네슘 조절, 요로 건강 사료",
        "설명": "고양이나 요로 문제가 있는 품종은 수분 섭취 관리가 중요해요."
    },
    "심장": {
        "성분": "타우린, 오메가3, 저나트륨 식단",
        "설명": "심장 질환 위험이 있는 품종은 나트륨과 지방 관리가 중요해요."
    },
    "치아": {
        "성분": "치석 관리 사료, 덴탈 간식, 저당 식단",
        "설명": "치아 질환이 쉬운 품종은 치석 관리가 필요해요."
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
        "제품명": "덴탈 케어 사료",
        "대상": "강아지",
        "추천 고민": "치아",
        "kcal_per_100g": 340,
        "가격": 33000,
        "용량": "2kg",
        "특징": "치석 관리, 구강 건강 도움"
    },
    {
        "제품명": "하트 케어 사료",
        "대상": "강아지",
        "추천 고민": "심장",
        "kcal_per_100g": 345,
        "가격": 41000,
        "용량": "2kg",
        "특징": "저나트륨, 심장 건강 관리"
    },
    {
        "제품명": "캣 유리너리 케어",
        "대상": "고양이",
        "추천 고민": "요로/신장",
        "kcal_per_100g": 350,
        "가격": 32000,
        "용량": "2kg",
        "특징": "요로 건강, 수분 섭취 관리"
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
    {
        "제품명": "캣 조인트 케어",
        "대상": "고양이",
        "추천 고민": "관절/뼈",
        "kcal_per_100g": 355,
        "가격": 39000,
        "용량": "2kg",
        "특징": "관절 건강 관리"
    },
    {
        "제품명": "캣 하트 케어",
        "대상": "고양이",
        "추천 고민": "심장",
        "kcal_per_100g": 340,
        "가격": 42000,
        "용량": "2kg",
        "특징": "타우린, 저나트륨 관리"
    },
]

feed_df = pd.DataFrame(FEED_DATA)
feed_df["100g당 가격"] = feed_df["가격"] / 20

# =========================
# 프로필 사진 함수
# =========================

def image_to_base64(uploaded_file):
    if uploaded_file is None:
        return None

    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode()


def show_profile_image(image_data, width=120):
    if image_data:
        st.image(
            f"data:image/png;base64,{image_data}",
            width=width
        )
    else:
        st.info("등록된 사진 없음")

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
        return "현재 체중이 낮은 편이라 충분한 영양 섭취가 중요해요."
    elif body_status == "적정":
        return "현재 상태를 유지할 수 있도록 일정한 급여량과 활동량을 관리해 주세요."
    else:
        return "체중 관리가 필요할 수 있어요. 간식량과 하루 총 칼로리를 함께 조절하는 것이 좋아요."


def disease_to_issues(disease):
    disease = str(disease)
    issues = []

    if any(word in disease for word in ["슬개골", "관절", "고관절", "디스크", "척추"]):
        issues.append("관절/뼈")

    if any(word in disease for word in ["피부", "피부염", "알레르기", "탈모", "눈물"]):
        issues.append("피부/모질")

    if any(word in disease for word in ["비만"]):
        issues.append("체중 조절")

    if any(word in disease for word in ["소화", "장"]):
        issues.append("소화/장")

    if any(word in disease for word in ["요로", "결석", "신장"]):
        issues.append("요로/신장")

    if any(word in disease for word in ["심장", "HCM", "DCM"]):
        issues.append("심장")

    if any(word in disease for word in ["치아", "치석"]):
        issues.append("치아")

    return issues


def recommend_feeds(species, user_issues, breed_info):
    disease_issues = disease_to_issues(breed_info["main_disease"])

    all_issues = []

    for issue in user_issues + disease_issues:
        if issue not in all_issues:
            all_issues.append(issue)

    result = feed_df[
        (feed_df["대상"] == species) &
        (feed_df["추천 고민"].isin(all_issues))
    ].copy()

    if result.empty:
        result = feed_df[feed_df["대상"] == species].copy()

    return result, disease_issues, all_issues


# =========================
# 세션 저장
# =========================

if "diet_results" not in st.session_state:
    st.session_state.diet_results = []

# =========================
# 입력 UI
# =========================

st.subheader("반려동물 프로필 등록")

with st.container(border=True):
    name = st.text_input("반려동물 이름", placeholder="예: 멍멍이")

    profile_image = st.file_uploader(
        "프로필 사진",
        type=["png", "jpg", "jpeg"],
        key="profile_image"
    )

    if profile_image:
        st.image(profile_image, caption="프로필 사진 미리보기", width=150)

    col1, col2 = st.columns(2)

    with col1:
        species = st.radio("종류", ["강아지", "고양이"], horizontal=True)

        breed_options = breed_df[
            breed_df["type"] == species
        ]["breed"].tolist()

        selected_breed = st.selectbox("품종", breed_options)

        age = st.number_input("나이 (세)", min_value=0, max_value=30, step=1)

    with col2:
        weight = st.number_input("몸무게 (kg)", min_value=0.0, step=0.1)
        neutered = st.checkbox("중성화 완료", value=True)
        body_status = st.selectbox("체형 상태", ["마른 편", "적정", "통통한 편"])
        activity = st.selectbox("활동량", ["낮음", "보통", "높음"])

    breed_info = breed_df[
        breed_df["breed"] == selected_breed
    ].iloc[0]

    with st.expander("선택한 품종 정보 보기", expanded=True):
        c1, c2, c3 = st.columns(3)

        c1.metric("크기", breed_info["size"])
        c2.metric("품종 활동량", breed_info["energy"])
        c3.metric("털 빠짐", breed_info["shedding"])

        st.write(f"🏥 대표 질환: **{breed_info['main_disease']}**")
        st.write(f"💰 예상 월 양육비: **{breed_info['cost']}**")
        st.write(f"⏳ 평균 수명: **{breed_info['life_span']}**")

    health_issues = st.multiselect(
        "추가로 신경 쓰고 싶은 건강 고민",
        ["관절/뼈", "피부/모질", "체중 조절", "소화/장", "눈물 자국", "요로/신장", "심장", "치아"],
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
        user_issues = health_issues.copy()
        disease_issues = disease_to_issues(breed_info["main_disease"])

        weight_control = (
            "체중 조절" in user_issues
            or "체중 조절" in disease_issues
            or body_status == "통통한 편"
        )

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

        _, disease_issues, all_issues = recommend_feeds(
            species,
            user_issues,
            breed_info
        )

        result = {
            "프로필 사진": image_to_base64(profile_image),
            "이름": name,
            "종류": species,
            "품종": selected_breed,
            "나이": age,
            "몸무게": weight,
            "중성화": "완료" if neutered else "안 함",
            "체형": body_status,
            "활동량": activity,
            "품종 크기": breed_info["size"],
            "품종 활동량": breed_info["energy"],
            "털 빠짐": breed_info["shedding"],
            "대표 질환": breed_info["main_disease"],
            "하루 권장 칼로리": round(mer),
            "RER": round(rer),
            "권장 사료량(g)": round(grams),
            "사용자 고민": ", ".join(user_issues) if user_issues else "없음",
            "품종 기반 고민": ", ".join(disease_issues) if disease_issues else "없음",
            "추천 기준": ", ".join(all_issues) if all_issues else "기본 관리"
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
    st.subheader(f"{latest['이름']} 맞춤 영양 결과")
    show_profile_image(latest.get("프로필 사진"), width=160)

    st.caption(
        f"{latest['종류']} · {latest['품종']} · "
        f"{latest['나이']}세 · {latest['몸무게']}kg"
    )

    m1, m2, m3 = st.columns(3)

    m1.metric("하루 권장 칼로리", f"{latest['하루 권장 칼로리']:,} kcal")
    m2.metric("RER", f"{latest['RER']:,} kcal")
    m3.metric("건사료 기준 급여량", f"{latest['권장 사료량(g)']} g")

    st.info(
        "일반 건사료 100g당 350kcal 기준으로 계산했어요. "
        "실제 급여량은 사료 포장지의 칼로리에 맞춰 조절해야 합니다."
    )

    st.write(get_body_message(latest["체형"]))

    if latest["품종 기반 고민"] != "없음":
        st.warning(
            f"선택한 품종의 대표 질환을 바탕으로 "
            f"**{latest['품종 기반 고민']}** 관리가 함께 추천됩니다."
        )

    # =========================
    # 건강 고민별 추천 영양 성분
    # =========================

    st.divider()
    st.subheader("건강 고민별 추천 영양 성분")

    issue_list = latest["추천 기준"].split(", ") if latest["추천 기준"] != "기본 관리" else []

    if not issue_list:
        st.write("특별한 건강 고민이 없다면 균형 잡힌 단백질, 지방, 비타민, 미네랄이 중요해요.")
    else:
        for issue in issue_list:
            if issue in NUTRIENT_GUIDE:
                guide = NUTRIENT_GUIDE[issue]

                with st.container(border=True):
                    st.markdown(f"### {issue}")
                    st.write(f"**추천 성분:** {guide['성분']}")
                    st.write(guide["설명"])

    # =========================
    # 품종 기반 사료 비교 검색
    # =========================

    st.divider()
    st.subheader("품종별 사료 비교")

    latest_breed_info = breed_df[
        breed_df["breed"] == latest["품종"]
    ].iloc[0]

    user_issues = (
        latest["사용자 고민"].split(", ")
        if latest["사용자 고민"] != "없음"
        else []
    )

    feed_result, disease_issues, all_issues = recommend_feeds(
        latest["종류"],
        user_issues,
        latest_breed_info
    )

    display_feed = feed_result.copy()

    display_feed["가격"] = display_feed["가격"].apply(
        lambda x: f"{x:,}원"
    )

    display_feed["100g당 가격"] = display_feed["100g당 가격"].apply(
        lambda x: f"{x:,.0f}원"
    )

    st.dataframe(
        display_feed[
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

    cheapest = feed_result.sort_values("100g당 가격").iloc[0]

    st.success(
        f"💰 가성비 추천 사료: **{cheapest['제품명']}** "
        f"({cheapest['100g당 가격']:.0f}원 / 100g)"
    )

    # =========================
    # 위험 음식 목록
    # =========================

    st.divider()
    st.subheader("주의해야 할 음식")

    danger_cols = st.columns(4)

    for col, food in zip(danger_cols * 3, DANGER_FOODS[latest["종류"]]):
        with col:
            st.error(food)

# =========================
# 다묘·다견 프로필 수정/삭제 관리
# =========================

if st.session_state.diet_results:

    st.divider()

    # ── DB 기반 목록 (영구 저장, 새로고침해도 유지) ──────────────────
    st.subheader("등록된 반려동물")
    st.caption("아래 목록은 계정에 저장되어 새로고침해도 유지되며, "
               "사이드바·건강 수첩과 연결됩니다.")
    db_pets = get_pets()
    if db_pets:
        db_rows = []
        for p in db_pets:
            db_rows.append({
                "이름": p["name"],
                "종류": p.get("species") or "-",
                "나이": p["age"],
                "몸무게(kg)": p["weight"],
                "중성화": "완료" if p.get("neutered") else "안 함",
                "하루 권장 칼로리": p.get("mer") or "-",
            })
        st.dataframe(pd.DataFrame(db_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("아직 DB에 저장된 반려동물이 없어요.")

    st.divider()

    # ── 세션 기반 분석 결과 (사진·고민 포함, 새로고침 시 사라짐) ──────
    st.subheader("이번 분석 결과")
    st.info("📷 사진·고민 등 상세 분석 결과는 **이번 접속 동안만** 보여집니다. "
            "(새로고침하면 사라져요. 이름·나이·몸무게 등 기본 정보는 위 '등록된 반려동물'에 영구 저장됩니다.)")

    result_df = pd.DataFrame(st.session_state.diet_results)

    display_df = result_df.drop(
        columns=["프로필 사진"],
        errors="ignore"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    profile_names = [
        f"{i + 1}. {pet['이름']} ({pet['품종']})"
        for i, pet in enumerate(st.session_state.diet_results)
    ]

    selected_profile = st.selectbox(
        "수정/삭제할 프로필 선택",
        profile_names
    )

    selected_index = profile_names.index(selected_profile)
    selected_pet = st.session_state.diet_results[selected_index]

    show_profile_image(selected_pet.get("프로필 사진"), width=140)

    with st.container(border=True):
        st.markdown(f"### ✏️ {selected_pet['이름']} 프로필 수정")

        edit_profile_image = st.file_uploader(
            "프로필 사진 변경",
            type=["png", "jpg", "jpeg"],
            key="edit_profile_image"
        )

        if edit_profile_image:
            st.image(
                edit_profile_image,
                caption="새 프로필 사진",
                width=150
            )

        edit_name = st.text_input(
            "이름 수정",
            value=selected_pet["이름"],
            key="edit_name"
        )

        edit_species = st.radio(
            "종류 수정",
            ["강아지", "고양이"],
            index=["강아지", "고양이"].index(selected_pet["종류"]),
            horizontal=True,
            key="edit_species"
        )

        edit_breed_options = breed_df[
            breed_df["type"] == edit_species
        ]["breed"].tolist()

        old_breed = selected_pet["품종"]

        if old_breed in edit_breed_options:
            breed_index = edit_breed_options.index(old_breed)
        else:
            breed_index = 0

        edit_breed = st.selectbox(
            "품종 수정",
            edit_breed_options,
            index=breed_index,
            key="edit_breed"
        )

        col1, col2 = st.columns(2)

        with col1:
            edit_age = st.number_input(
                "나이 수정",
                min_value=0,
                max_value=30,
                step=1,
                value=int(selected_pet["나이"]),
                key="edit_age"
            )

            edit_weight = st.number_input(
                "몸무게 수정",
                min_value=0.1,
                step=0.1,
                value=float(selected_pet["몸무게"]),
                key="edit_weight"
            )

        with col2:
            edit_neutered = st.checkbox(
                "중성화 완료",
                value=True if selected_pet["중성화"] == "완료" else False,
                key="edit_neutered"
            )

            edit_body_status = st.selectbox(
                "체형 상태 수정",
                ["마른 편", "적정", "통통한 편"],
                index=["마른 편", "적정", "통통한 편"].index(selected_pet["체형"]),
                key="edit_body_status"
            )

            edit_activity = st.selectbox(
                "활동량 수정",
                ["낮음", "보통", "높음"],
                index=["낮음", "보통", "높음"].index(selected_pet["활동량"]),
                key="edit_activity"
            )

        old_user_issues = (
            selected_pet["사용자 고민"].split(", ")
            if selected_pet["사용자 고민"] != "없음"
            else []
        )

        edit_health_issues = st.multiselect(
            "건강 고민 수정",
            ["관절/뼈", "피부/모질", "체중 조절", "소화/장", "눈물 자국", "요로/신장", "심장", "치아"],
            default=old_user_issues,
            key="edit_health_issues"
        )

        b1, b2 = st.columns(2)

        with b1:
            if st.button("수정 저장", type="primary"):
                edit_breed_info = breed_df[
                    breed_df["breed"] == edit_breed
                ].iloc[0]

                edit_disease_issues = disease_to_issues(
                    edit_breed_info["main_disease"]
                )

                edit_weight_control = (
                    "체중 조절" in edit_health_issues
                    or "체중 조절" in edit_disease_issues
                    or edit_body_status == "통통한 편"
                )

                edit_rer, edit_mer = calc_calories(
                    edit_weight,
                    edit_age,
                    edit_species,
                    edit_neutered,
                    edit_weight_control
                )

                if edit_activity == "낮음":
                    edit_mer *= 0.9
                elif edit_activity == "높음":
                    edit_mer *= 1.1

                edit_grams = edit_mer / 3500 * 1000

                _, edit_disease_issues, edit_all_issues = recommend_feeds(
                    edit_species,
                    edit_health_issues,
                    edit_breed_info
                )

                st.session_state.diet_results[selected_index] = {
                    "프로필 사진": (
                        image_to_base64(edit_profile_image)
                        if edit_profile_image
                        else selected_pet.get("프로필 사진")
                    ),
                    "이름": edit_name,
                    "종류": edit_species,
                    "품종": edit_breed,
                    "나이": edit_age,
                    "몸무게": edit_weight,
                    "중성화": "완료" if edit_neutered else "안 함",
                    "체형": edit_body_status,
                    "활동량": edit_activity,
                    "품종 크기": edit_breed_info["size"],
                    "품종 활동량": edit_breed_info["energy"],
                    "털 빠짐": edit_breed_info["shedding"],
                    "대표 질환": edit_breed_info["main_disease"],
                    "하루 권장 칼로리": round(edit_mer),
                    "RER": round(edit_rer),
                    "권장 사료량(g)": round(edit_grams),
                    "사용자 고민": ", ".join(edit_health_issues) if edit_health_issues else "없음",
                    "품종 기반 고민": ", ".join(edit_disease_issues) if edit_disease_issues else "없음",
                    "추천 기준": ", ".join(edit_all_issues) if edit_all_issues else "기본 관리"
                }

                upsert_pet(
                    name=edit_name,
                    species=edit_species,
                    age=edit_age,
                    weight=edit_weight,
                    neutered=edit_neutered,
                    mer=round(edit_mer)
                )

                st.success("프로필이 수정되었습니다.")
                st.rerun()

        with b2:
            if st.button("삭제하기"):
                # 세션과 DB 모두에서 삭제 (불일치 방지)
                pet_name = st.session_state.diet_results[selected_index].get("이름")
                del st.session_state.diet_results[selected_index]
                if pet_name:
                    for p in get_pets():
                        if p["name"] == pet_name:
                            delete_pet(p["id"])
                            break
                st.success("프로필이 삭제되었습니다.")
                st.rerun()

    if st.session_state.diet_results:
        result_df = pd.DataFrame(st.session_state.diet_results)

        total_kcal = result_df["하루 권장 칼로리"].sum()
        total_gram = result_df["권장 사료량(g)"].sum()

        c1, c2 = st.columns(2)

        c1.metric("전체 하루 필요 칼로리", f"{total_kcal:,} kcal")
        c2.metric("전체 하루 예상 사료량", f"{total_gram:,} g")