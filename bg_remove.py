import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
from io import BytesIO
import base64
import os
import traceback
import time

st.set_page_config(layout="wide", page_title="Image Background Remover")

st.write("## Remove background from your image")
st.write(
    ":dog: Thử tải lên một hình ảnh để xem nền bị xóa một cách “thần kỳ”. Bạn có thể tải về hình ảnh chất lượng đầy đủ từ thanh bên."
)
st.sidebar.write("## Upload and download :gear:")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Max dimensions for processing
MAX_IMAGE_SIZE = 2000  # pixels

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# Resize image while maintaining aspect ratio
def resize_image(image, max_size):
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image
    
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    return image.resize((new_width, new_height), Image.LANCZOS)

@st.cache_data
def process_image(image_bytes):
    """Xử lý hình ảnh **với cơ chế lưu trữ tạm (cache)** để tránh việc xử lý **trùng lặp không cần thiết**.
"""
    try:
        image = Image.open(BytesIO(image_bytes))
        # Resize large images to prevent memory issues
        resized = resize_image(image, MAX_IMAGE_SIZE)
        # Process the image
        fixed = remove(resized)
        return image, fixed
    except Exception as e:
        st.error(f"Lỗi xử lý hình ảnh: {str(e)}")
        return None, None

def fix_image(upload):
    try:
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        status_text.text("Đang tải...")
        progress_bar.progress(10)
        
        # Read image bytes
        if isinstance(upload, str):
            # Default image path
            if not os.path.exists(upload):
                st.error(f"Ảnh không tìm thấy: {upload}")
                return
            with open(upload, "rb") as f:
                image_bytes = f.read()
        else:
            # Uploaded file
            image_bytes = upload.getvalue()
        
        status_text.text("Đang xử lý...")
        progress_bar.progress(30)
        
        # Process image (using cache if available)
        image, fixed = process_image(image_bytes)
        if image is None or fixed is None:
            return
        
        progress_bar.progress(80)
        status_text.text("Đang hiển thị kết quả")
        
        # Display images
        col1.write("Ảnh gốc :camera:")
        col1.image(image)
        
        col2.write("Ảnh đã xử lý:wrench:")
        col2.image(fixed)
        
        # Prepare download button
        st.sidebar.markdown("\n")
        st.sidebar.download_button(
            "Tải ảnh đã xử lý", 
            convert_image(fixed), 
            "fixed.png", 
            "image/png"
        )
        
        progress_bar.progress(100)
        processing_time = time.time() - start_time
        status_text.text(f"Hoàn thành trong {processing_time:.2f} giây")
        
    except Exception as e:
        st.error(f"Đã có lỗi: {str(e)}")
        st.sidebar.error("Failed to process image")
        # Log the full error for debugging
        print(f"Lỗi khi sửa ảnh: {traceback.format_exc()}")

# UI Layout
col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Tải ảnh lên", type=["png", "jpg", "jpeg"])

# Information about limitations
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write("""
    - Size file tối đa: 10MB
    - Ảnh lớn sẽ tự động được chỉnh sửa size
    - File được hỗ trợ: PNG, JPG, JPEG
    - Thời gian xử lý ảnh phụ thuộc vào độ lớn
    """)

# Process the image
if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error(f"File quá lớn, xin hãy up file nhỏ hơn: {MAX_FILE_SIZE/1024/1024:.1f}MB.")
    else:
        fix_image(upload=my_upload)
else:
    # Try default images in order of preference
    default_images = ["./zebra.jpg", "./wallaby.png"]
    for img_path in default_images:
        if os.path.exists(img_path):
            fix_image(img_path)
            break
    else:
        st.info("Hãy tải ảnh lên để bắt đầu!")
