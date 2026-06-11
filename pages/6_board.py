import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth

auth.login_widget()

st.title("이야기 나누기")
st.markdown("반려동물을 키우며 쌓인 노하우나 고민을 다른 보호자들과 나눠요.")

# 현재 접속자 정보 표시 (db.py 로직 활용)
user_id = db.current_user_id()
if user_id == 1:
    st.info("지금은 게스트로 보고 있어요. 닉네임으로 활동하려면 왼쪽에서 로그인해 주세요.")
else:
    nickname = st.session_state.get('nickname', '회원')
    st.success(f"{nickname}님으로 접속 중이에요.")

st.divider()

# ── 새 글 작성 영역 ──
with st.expander("새 글 쓰기"):
    with st.form("new_post_form", clear_on_submit=True):
        title = st.text_input("제목", placeholder="제목을 입력하세요")
        content = st.text_area("내용", placeholder="내용을 입력하세요")
        submitted = st.form_submit_button("글 등록")
        
        if submitted:
            if title.strip() and content.strip():
                db.add_post(title, content)
                st.toast("글을 올렸어요.")
                st.rerun()
            else:
                st.warning("제목과 내용을 모두 입력해주세요.")

st.divider()

# ── 게시글 목록 및 댓글 영역 ──
st.subheader("전체 글")
posts = db.get_posts()

if not posts:
    st.info("아직 등록된 게시글이 없습니다. 첫 글의 주인공이 되어보세요!")
else:
    my_id = db.current_user_id()
    for post in posts:
        # 익명 사용자의 경우 이름을 '익명(게스트)'로 고정
        display_name = "익명(게스트)" if post['auth_kind'] == 'guest' else post['author_name']

        # 각 글을 Expander(접기/펼치기) 뷰로 생성
        with st.expander(f"{post['title']}  ·  {display_name}  ·  {post['created_at'][:16]}"):
            st.markdown(post['content'])

            # ─ 본인 글이면 삭제 버튼 ─
            if post['user_id'] == my_id:
                if st.button("글 삭제", key=f"del_post_{post['id']}"):
                    db.delete_post(post['id'])
                    st.toast("게시글을 삭제했어요.")
                    st.rerun()

            st.divider()

            # ─ 댓글 영역 ─
            comments = db.get_comments(post['id'])
            if comments:
                for c in comments:
                    c_name = "익명(게스트)" if c['auth_kind'] == 'guest' else c['author_name']
                    cc1, cc2 = st.columns([6, 1])
                    cc1.caption(f"**{c_name}**: {c['content']} ({c['created_at'][:16]})")
                    # 본인 댓글이면 삭제 버튼
                    if c['user_id'] == my_id:
                        if cc2.button("삭제", key=f"del_comment_{c['id']}"):
                            db.delete_comment(c['id'])
                            st.toast("댓글을 삭제했어요.")
                            st.rerun()
            else:
                st.caption("등록된 댓글이 없습니다.")

            # ─ 새 댓글 작성 폼 ─
            # Streamlit의 form 충돌을 막기 위해 post['id']를 key로 활용
            with st.form(key=f"comment_form_{post['id']}", clear_on_submit=True):
                c_col1, c_col2 = st.columns([4, 1])
                with c_col1:
                    comment_text = st.text_input("댓글 쓰기", label_visibility="collapsed", placeholder="댓글을 남겨보세요")
                with c_col2:
                    comment_submitted = st.form_submit_button("등록")

                if comment_submitted:
                    if comment_text.strip():
                        db.add_comment(post['id'], comment_text)
                        st.rerun()
                    else:
                        st.warning("댓글 내용을 입력하세요.")