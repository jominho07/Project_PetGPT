import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os

# 1. 프로젝트 최상위 폴더(루트) 절대 경로 계산
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
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 파일 로드
CSV_PATH = os.path.join(BASE_DIR, "data", "stores.csv")
df = load_data(CSV_PATH)

if df.empty:
    st.warning("표시할 가게 데이터가 없습니다. data 폴더 안에 stores.csv 파일이 올바르게 있는지 확인해주세요.")
else:
    # ★ [이 부분이 추가되었습니다!] 
    # utils.py의 공통 함수들이 영문 컬럼명을 요구하므로, 기존 한글 데이터를 영문 컬럼으로 복사해줍니다.
    df['sido'] = df['시도']
    df['sigungu'] = df['시군구']
    df['dong'] = df['동']

    # 3. 지역 선택 필터 적용 (이제 에러가 나지 않습니다!)
    sido, sigungu, dong = region_selectors(df, key_prefix="shop")
    filtered = filter_places(df, sido, sigungu, dong)
    
    # 4. 지도 및 목록 렌더링
    st.subheader(f"📍 검색 결과: {len(filtered)}개의 용품점")
    
    if not filtered.empty:
        avg_lat = filtered['위도'].mean()
        avg_lon = filtered['경도'].mean()
        
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)
        
        for idx, row in filtered.iterrows():
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
                tooltip=row['가게명'],
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        
        st_folium(m, width=700, height=500)
        
        st.divider()
        st.write("📋 **가게 목록**")
        st.dataframe(filtered[['가게명', '시군구', '동', '전화번호', '특징']], hide_index=True)

    else:
        st.info("선택한 지역에 등록된 용품점이 없습니다.")