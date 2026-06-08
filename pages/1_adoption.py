import streamlit as st
import pandas as pd
import sys, os
import math
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth

auth.login_widget()

st.title("🏠 나에게 꼭 맞는 가족 찾기")
st.write("간단한 설문을 통해 운명의 반려동물을 추천해 드립니다.")

st.divider()

# =========================
# CSV 로드
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BREEDS_PATH = os.path.join(BASE_DIR, "data", "breeds.csv")
PETSHOP_PATH = os.path.join(BASE_DIR, "data", "petshop.csv")

df = pd.read_csv(BREEDS_PATH)
shop_df = pd.read_csv(PETSHOP_PATH)

df["allergy_friendly"] = (
    df["allergy_friendly"]
    .astype(str)
    .str.lower()
    .eq("true")
)

# =========================
# 거리 계산 함수
# =========================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

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

if "last_pet_type" not in st.session_state:
    st.session_state.last_pet_type = pet_type

if st.session_state.last_pet_type != pet_type:
    st.session_state.top3 = None
    st.session_state.selected = None
    st.session_state.last_pet_type = pet_type

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
# TOP3 출력
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

                    if st.button("상세 보기", key=f"dog_{row['breed']}"):
                        st.session_state.selected = row

        st.success("🏆 고양이 TOP 3")

        cols = st.columns(3)

        for col, (_, row) in zip(cols, cat_top3.iterrows()):

            with col:
                with st.container(border=True):

                    st.markdown(f"### 😺 {row['breed']}")
                    st.write(f"📏 크기: {row['size']}")

                    if st.button("상세 보기", key=f"cat_{row['breed']}"):
                        st.session_state.selected = row

    else:

        st.success("🏆 추천 TOP 3")

        cols = st.columns(3)

        for col, (_, row) in zip(cols, st.session_state.top3.iterrows()):

            with col:
                with st.container(border=True):

                    emoji = "🐶" if row["type"] == "강아지" else "😺"

                    st.markdown(f"### {emoji} {row['breed']}")
                    st.write(f"📏 크기: {row['size']}")

                    if st.button("상세 보기", key=row["breed"]):
                        st.session_state.selected = row

# =========================
# 상세 정보 + 위치 기반 입양처
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

    st.divider()
    st.subheader("🗺 내 위치 기반 입양 가능 장소")

    location = get_geolocation()

    if location is None:
        st.warning("📍 브라우저에서 위치 권한을 허용해주세요.")

    else:
        user_lat = location["coords"]["latitude"]
        user_lon = location["coords"]["longitude"]

        st.success(f"현재 위치: {user_lat:.4f}, {user_lon:.4f}")

        selected_type = pet["type"]
        selected_breed = pet["breed"]

        filtered_shop = shop_df[
            (shop_df["animal_type"] == selected_type) &
            (
                shop_df["breed"]
                .astype(str)
                .str.contains(selected_breed, na=False)
            )
        ].copy()

        if filtered_shop.empty:
            st.warning(f"현재 {selected_breed} 입양 가능 장소가 없습니다.")

        else:
            filtered_shop["distance"] = filtered_shop.apply(
                lambda r: haversine(
                    user_lat,
                    user_lon,
                    r["lat"],
                    r["lon"]
                ),
                axis=1
            )

            filtered_shop = filtered_shop.sort_values("distance")

            nearest = filtered_shop.iloc[0]

            st.success(
                f"가장 가까운 추천 입양처는 "
                f"**{nearest['name']}** 입니다. "
                f"거리: {nearest['distance']:.2f}km"
            )

            radius = st.slider("검색 반경 km", 1, 30, 10)

            nearby = filtered_shop[
                filtered_shop["distance"] <= radius
            ].sort_values("distance")

            m = folium.Map(
                location=[user_lat, user_lon],
                zoom_start=12
            )

            folium.Marker(
                [user_lat, user_lon],
                popup="내 위치",
                tooltip="내 위치",
                icon=folium.Icon(color="blue", icon="user")
            ).add_to(m)

            for _, r in nearby.iterrows():

                marker_color = (
                    "red"
                    if r["name"] == nearest["name"]
                    else "green"
                )

                folium.Marker(
                    [r["lat"], r["lon"]],
                    popup=f"""
                    <b>{r['name']}</b><br>
                    동물: {r['animal_type']}<br>
                    입양 가능 품종: {r['breed']}<br>
                    거리: {r['distance']:.2f}km
                    """,
                    tooltip=r["name"],
                    icon=folium.Icon(
                        color=marker_color,
                        icon="home"
                    )
                ).add_to(m)

            st_folium(m, width=700, height=500)

            st.subheader("📌 가까운 입양처 목록")

            if nearby.empty:
                st.warning("검색 반경 안에 입양처가 없습니다.")
            else:
                for _, r in nearby.iterrows():
                    st.write(f"""
                    🏠 **{r['name']}**
                    - 동물: {r['animal_type']}
                    - 입양 가능 품종: {r['breed']}
                    - 거리: {r['distance']:.2f}km
                    """)

    if st.button("닫기"):
        st.session_state.selected = None
        st.rerun()
