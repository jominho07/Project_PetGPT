import streamlit as st
from db import get_pets
import auth

st.set_page_config(
    page_title="Pet-GPT: 반려동물 통합 케어",
    page_icon="🐾",
    layout="wide",
)

st.title("🐾 반려동물 생애주기 통합 관리 서비스")
st.subheader("입양부터 마지막 순간까지, Pet-GPT가 함께합니다.")
st.info("아래 서비스 카드를 누르거나 왼쪽 사이드바 메뉴에서 원하는 서비스를 선택하세요.")

st.divider()

# ── 서비스 한눈에 보기 (카드를 누르면 해당 페이지로 이동) ───────────
st.markdown("### 제공 서비스")

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.page_link("pages/1_adoption.py", label="**🏠 가족 찾기**")
        st.caption("설문 기반으로 나에게 맞는 반려동물을 추천")
with c2:
    with st.container(border=True):
        st.page_link("pages/2_diet.py", label="**🥗 맞춤 식단**")
        st.caption("나이·몸무게로 하루 권장 칼로리를 계산")
with c3:
    with st.container(border=True):
        st.page_link("pages/4_health.py", label="**📒 건강 수첩**")
        st.caption("케어 일정·진료 기록·투약을 관리")

c4, c5, c6 = st.columns(3)
with c4:
    with st.container(border=True):
        st.page_link("pages/3_shop.py", label="**🛍️ 용품점 찾기**")
        st.caption("내 주변 펫 용품점·미용점을 안내")
with c5:
    with st.container(border=True):
        st.page_link("pages/5_memorial.py", label="**🕯️ 마지막 안녕**")
        st.caption("장례식장 안내 + 추억 앨범 기록")
with c6:
    with st.container(border=True):
        st.page_link("pages/6_board.py", label="**💬 소통 게시판**")
        st.caption("반려인들과 꿀팁·고민을 나누는 공간")

st.divider()

# ── 내 반려동물 (본문에 크게 표시) ─────────────────────────────────
st.markdown("### 🐶 내 반려동물")

pets = get_pets()
if pets:
    # 한 줄에 최대 3마리씩 카드로 표시
    for i in range(0, len(pets), 3):
        row_pets = pets[i:i + 3]
        cols = st.columns(3)
        for col, p in zip(cols, row_pets):
            with col:
                with st.container(border=True):
                    st.markdown(f"#### 🐾 {p['name']}")
                    species = p.get("species") or "반려동물"
                    st.write(f"종류: {species}")
                    st.write(f"나이: {p['age']}세  ·  몸무게: {p['weight']}kg")
                    neutered = "✅ 완료" if p.get("neutered") else "❌ 안 함"
                    st.caption(f"중성화: {neutered}")
else:
    st.info("아직 등록된 반려동물이 없어요. '🥗 맞춤 식단' 페이지에서 등록해 보세요.")

# ── 사이드바 (로그인 + 내 반려동물은 auth.login_widget 이 처리) ─────
auth.login_widget()