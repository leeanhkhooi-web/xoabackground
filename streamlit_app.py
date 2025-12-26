import streamlit as st
from bg_remove import remove_bg

st.set_page_config(page_title="Xoá nền ảnh")

st.title("🖼️ Xoá nền ảnh")

uploaded = st.file_uploader("Tải ảnh lên", type=["png", "jpg", "jpeg"])

if uploaded:
    result = remove_bg(uploaded)
    st.image(result, caption="Ảnh đã xoá nền")
