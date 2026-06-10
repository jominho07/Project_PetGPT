import streamlit as st
from db import get_pets, delete_pet, get_upcoming_schedules
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

# ── 로그인 사용자: 다가오는 케어 일정 D-day ────────────────────────
if auth.is_logged_in():
    upcoming = get_upcoming_schedules(days_ahead=30)
    if upcoming:
        st.markdown("### ⏰ 다가오는 케어 일정")
        # 최대 4개까지 카드로
        show = upcoming[:4]
        cols = st.columns(len(show))
        for col, s in zip(cols, show):
            with col:
                with st.container(border=True):
                    d = s["d_day"]
                    if d == 0:
                        dday = "🔴 D-DAY"
                    else:
                        dday = f"D-{d}"
                    pet_name = (s.get("pet_name") or "").strip() or "우리 아이"
                    st.markdown(f"#### {dday}")
                    st.write(f"🐾 {pet_name}")
                    st.caption(f"{s['care_type']} · {s['next_due']}")
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
                    # 로그인한 사용자만 삭제 가능
                    if auth.is_logged_in():
                        if st.button("🗑️ 삭제", key=f"del_pet_{p['id']}"):
                            delete_pet(p["id"])
                            st.toast(f"'{p['name']}' 정보를 삭제했어요.")
                            st.rerun()
    st.caption("ℹ️ 정보를 수정하려면 '🥗 맞춤 식단' 페이지에서 같은 이름으로 다시 등록하면 갱신돼요.")
else:
    st.info("아직 등록된 반려동물이 없어요. '🥗 맞춤 식단' 페이지에서 등록해 보세요.")

# ── 사이드바 (로그인 + 내 반려동물은 auth.login_widget 이 처리) ─────
auth.login_widget()