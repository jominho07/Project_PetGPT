import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os

# 1. 프로젝트 최상위 폴더(루트) 절대 경로 계산 (현재 파일 위치 기준 2단계 위)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 프로젝트 루트의 utils.py 를 import 할 수 있도록 경로 추가
sys.path.append(BASE_DIR)

import auth
from utils import load_places, region_selectors, filter_places

auth.login_widget()

st.title("🛍️ 내 주변 펫 용품점 찾기")
st.write("내 위치(시/군/구/동)를 선택하면 가까운 반려동물 용품점을 지도에 표시해 드립니다.")

st.divider()

# 2. 데이터 로드 함수 정의
@st.cache_data
def load_data(file_path):
    try:
        # utf-8-sig는 한글 깨짐을 방지하고 눈에 안 보이는 공백/BOM을 제거합니다.
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # 글자 앞뒤에 혹시나 들어가 있을지 모르는 모든 공백 제거 (글자 사이 공백 제외)
        df.columns = df.columns.str.strip() 
        
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# ★ [수정 및 추가된 부분] 파일의 절대 경로를 생성하고 함수를 호출하여 df에 대입합니다.
CSV_PATH = os.path.join(BASE_DIR, "data", "stores.csv")
df = load_data(CSV_PATH)

# 3. 데이터가 정상적으로 로드되었는지 확인 후 렌더링
if df.empty:
    st.warning("표시할 가게 데이터가 없습니다. data 폴더 안에 stores.csv 파일이 올바르게 있는지 확인해주세요.")
else:
    # 4. 지역 선택 필터 적용
    sido, sigungu, dong = region_selectors(df, key_prefix="shop")
    filtered = filter_places(df, sido, sigungu, dong)
    
    # 5. 지도 및 목록 렌더링
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