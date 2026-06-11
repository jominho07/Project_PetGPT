import streamlit as st

st.set_page_config(
    page_title="Pet-GPT",
    page_icon="🐾",
    layout="wide",
)

# 사이드바 메뉴에 보일 이름(title)을 한글로 지정한다.
# 파일 이름은 영어 그대로 두되, 메뉴 라벨만 한글로 바꾸는 방식.
home = st.Page("home.py", title="홈", default=True)
adoption = st.Page("pages/1_adoption.py", title="가족 찾기")
diet = st.Page("pages/2_diet.py", title="맞춤 식단")
shop = st.Page("pages/3_shop.py", title="용품점 찾기")
health = st.Page("pages/4_health.py", title="건강 수첩")
memorial = st.Page("pages/5_memorial.py", title="마지막 인사")
board = st.Page("pages/6_board.py", title="이야기 나누기")

pg = st.navigation([home, adoption, diet, shop, health, memorial, board])
pg.run()
