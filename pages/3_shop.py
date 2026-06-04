import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 프로젝트 루트의 utils.py 를 import 할 수 있도록 경로 추가
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
from utils import load_places, region_selectors, filter_places

auth.login_widget()

st.title("🛍️ 내 주변 펫 용품점 찾기")
st.write("내 위치(시/군/구/동)를 선택하면 가까운 반려동물 용품점을 지도에 표시해 드립니다.")

st.divider()

# 1. 데이터 로드 (위도, 경도 컬럼이 필수)
# utils.py의 load_places 대신 직접 pandas로 로드하는 예시입니다.
# utils.py를 그대로 사용하셔도 됩니다 (단, 반환값이 pandas DataFrame이어야 함)
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_data("stores.csv") # 실제 경로에 맞게 수정

if df.empty:
    st.warning("표시할 가게 데이터가 없습니다.")
else:
    # 2. 지역 선택 필터 적용
    # utils.py 의 region_selectors 와 filter_places 를 사용한다고 가정
    sido, sigungu, dong = region_selectors(df, key_prefix="shop")
    filtered = filter_places(df, sido, sigungu, dong)
    
    # 3. 지도 및 목록 렌더링
    st.subheader(f"📍 검색 결과: {len(filtered)}개의 용품점")
    
    if not filtered.empty:
        # 지도의 초기 중심점을 필터링된 데이터의 평균 위경도로 설정
        avg_lat = filtered['위도'].mean()
        avg_lon = filtered['경도'].mean()
        
        # Folium 지도 객체 생성 (zoom_start는 확대 정도)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)
        
        # 필터링된 각 가게 위치에 마커 추가
        for idx, row in filtered.iterrows():
            # 팝업에 들어갈 내용 (HTML 형식으로 작성 가능)
            popup_html = f"""
            <div style='width: 200px'>
                <h4>{row['가게명']}</h4>
                <p><b>위치:</b> {row['시도']} {row['시군구']} {row['동']}</p>
                <p><b>전화:</b> {row['전화번호']}</p>
                <p><b>특징:</b> {row['특징']}</p>
            </div>
            """
            
            folium.Marker(
                [row['위도'], row['경도']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=row['가게명'], # 마커에 마우스를 올렸을 때 보이는 이름
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        
        # Streamlit 화면에 지도 출력 (width 조절 가능)
        st_folium(m, width=700, height=500)
        
        # (선택) 하단에 리스트 형태로도 정보 제공
        st.divider()
        st.write("📋 **가게 목록**")
        st.dataframe(filtered[['가게명', '시군구', '동', '전화번호', '특징']], hide_index=True)

    else:
        st.info("선택한 지역에 등록된 용품점이 없습니다.")