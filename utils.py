"""위치 기반 매장/시설 검색 공통 헬퍼.

stores.py 와 memorial.py 가 동일한 UI 패턴(시/도 → 시군구 → 동 필터 후
지도 + 목록 표시)을 공유하므로 여기에 모아둔다.
"""
import os
import pandas as pd
import streamlit as st

# 이 파일(utils.py)이 있는 폴더 기준으로 data 경로를 잡는다.
# (어느 페이지에서 import 하든 같은 경로를 가리키도록)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE_DIR, "data")


@st.cache_data
def load_places(csv_name):
    """data/<csv_name> 을 DataFrame 으로 읽어온다.

    @st.cache_data 덕분에 매 상호작용마다 파일을 다시 읽지 않는다.
    """
    path = os.path.join(_DATA_DIR, csv_name)
    df = pd.read_csv(path)
    return df


def region_selectors(df, key_prefix=""):
    """시/도 -> 시군구 -> 동 3단계 드롭다운을 그리고 (시도, 시군구, 동) 반환.

    - 시군구와 동에 "전체" 선택지가 있다.
    - 시군구가 "전체"면 동은 "전체"로 고정되고 비활성화된다.
    CSV 의 한글 컬럼명(시도/시군구/동)을 사용한다.
    """
    c1, c2, c3 = st.columns(3)

    with c1:
        sido_list = sorted(df["시도"].dropna().unique())
        sido = st.selectbox("시/도", sido_list, key=f"{key_prefix}_sido")

    with c2:
        sigungu_pool = df[df["시도"] == sido]["시군구"].dropna().unique()
        sigungu_list = ["전체"] + sorted(sigungu_pool)
        sigungu = st.selectbox("시/군/구", sigungu_list, key=f"{key_prefix}_sigungu")

    with c3:
        if sigungu == "전체":
            dong = st.selectbox("동/읍/면", ["전체"], key=f"{key_prefix}_dong",
                                disabled=True)
        else:
            dong_pool = df[(df["시도"] == sido) & (df["시군구"] == sigungu)]["동"].dropna().unique()
            dong_list = ["전체"] + sorted(dong_pool)
            dong = st.selectbox("동/읍/면", dong_list, key=f"{key_prefix}_dong")

    return sido, sigungu, dong


def filter_places(df, sido, sigungu, dong):
    """선택한 행정구역으로 DataFrame 을 필터링한다. (한글 컬럼명 사용)

    "전체" 는 해당 단계의 필터를 적용하지 않는다는 뜻.
    """
    result = df.copy()
    if sido and sido != "전체":
        result = result[result["시도"] == sido]
    if sigungu and sigungu != "전체":
        result = result[result["시군구"] == sigungu]
    if dong and dong != "전체":
        result = result[result["동"] == dong]
    return result.reset_index(drop=True)


def render_results(df, kind_label="매장"):
    """필터된 결과를 지도 + 카드 목록으로 표시한다."""
    if df.empty:
        st.info(f"선택한 지역에 등록된 {kind_label}이(가) 아직 없어요. "
                "시/군/구나 동을 바꿔보거나 '전체'로 검색해 보세요.")
        return

    st.write(f"**📍 검색 결과 {len(df)}곳**")
    st.map(df[["lat", "lon"]])

    st.markdown(f"#### {kind_label} 목록")
    for _, row in df.iterrows():
        with st.container(border=True):
            st.write(f"**{row['name']}**")
            st.caption(
                f"📍 {row['sigungu']} {row['dong']}  ·  "
                f"🏷️ {row['tags']}  ·  ☎ {row['phone']}"
            )