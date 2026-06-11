import streamlit as st
from db import get_pets, delete_pet, get_upcoming_schedules
import auth

st.set_page_config(
    page_title="Pet-GPT",
    page_icon="🐾",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 3rem; max-width: 1100px; }
    h1 { font-weight: 700; letter-spacing: -0.5px; }
    h3 { font-weight: 600; }
    [data-testid="stPageLink"] a { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("우리 아이의 평생을 함께")
st.write("입양부터 마지막 인사까지, 반려동물과 함께하는 모든 순간을 한곳에서 돌봐요.")

st.divider()

# ── 로그인 사용자: 다가오는 케어 일정 ──────────────────────────────
if auth.is_logged_in():
    upcoming = get_upcoming_schedules(days_ahead=30)
    if upcoming:
        st.markdown("### 곧 다가오는 일정")
        show = upcoming[:4]
        cols = st.columns(len(show))
        for col, s in zip(cols, show):
            with col:
                with st.container(border=True):
                    d = s["d_day"]
                    dday = "오늘" if d == 0 else f"{d}일 뒤"
                    pet_name = (s.get("pet_name") or "").strip() or "우리 아이"
                    st.markdown(f"#### {dday}")
                    st.write(f"{pet_name} · {s['care_type']}")
                    st.caption(s["next_due"])
        st.divider()

# ── 서비스 메뉴 (카드를 누르면 해당 페이지로 이동) ──────────────────
st.markdown("### 무엇을 도와드릴까요")

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.page_link("pages/1_adoption.py", label="가족 찾기")
        st.caption("몇 가지 질문에 답하면 잘 맞는 반려동물을 추천해 드려요.")
with c2:
    with st.container(border=True):
        st.page_link("pages/2_diet.py", label="맞춤 식단")
        st.caption("나이와 몸무게에 맞는 하루 권장 칼로리를 계산해요.")
with c3:
    with st.container(border=True):
        st.page_link("pages/4_health.py", label="건강 수첩")
        st.caption("케어 일정과 병원 기록, 복용 중인 약을 관리해요.")

c4, c5, c6 = st.columns(3)
with c4:
    with st.container(border=True):
        st.page_link("pages/3_shop.py", label="용품점 찾기")
        st.caption("가까운 반려동물 용품점과 미용실을 찾아봐요.")
with c5:
    with st.container(border=True):
        st.page_link("pages/5_memorial.py", label="마지막 인사")
        st.caption("장례식장 안내와 함께 추억을 기록할 수 있어요.")
with c6:
    with st.container(border=True):
        st.page_link("pages/6_board.py", label="이야기 나누기")
        st.caption("다른 보호자들과 고민이나 정보를 나눠요.")

st.divider()

# ── 내 반려동물 ────────────────────────────────────────────────────
hc1, hc2 = st.columns([3, 2])
with hc1:
    st.markdown("### 우리 아이들")
with hc2:
    st.page_link("pages/2_diet.py", label="반려동물 등록·수정하기")

pets = get_pets()
if pets:
    for i in range(0, len(pets), 3):
        row_pets = pets[i:i + 3]
        cols = st.columns(3)
        for col, p in zip(cols, row_pets):
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {p['name']}")
                    species = p.get("species") or "반려동물"
                    st.write(f"{species} · {p['age']}세 · {p['weight']}kg")
                    neutered = "중성화 완료" if p.get("neutered") else "중성화 안 함"
                    st.caption(neutered)
                    if auth.is_logged_in():
                        if st.button("삭제", key=f"del_pet_{p['id']}"):
                            delete_pet(p["id"])
                            st.toast(f"{p['name']} 정보를 삭제했어요.")
                            st.rerun()
    st.caption("정보를 바꾸려면 맞춤 식단 페이지에서 같은 이름으로 다시 등록하면 돼요.")
else:
    st.info("아직 등록한 반려동물이 없어요. 위의 등록하기를 눌러 첫 아이를 추가해 보세요.")

auth.login_widget()