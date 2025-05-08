# 제주 시설 지도 핀 자동화 도구 (Streamlit Cloud 또는 로컬 실행)
# - PNG 지도 이미지와 xlsx 시설 목록 업로드
# - 위경도 기반 핀 시각화
# - 서비스 유형별 색상 구분

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io

try:
    import streamlit as st
except ImportError:
    raise SystemExit("❗ Streamlit 모듈이 설치되지 않았습니다. 로컬 환경이나 Streamlit Cloud에서 실행하세요.")

# 기준점 2개로 위경도 → 픽셀 좌표 변환 기준
geo_refs = {
    "airport": {"lat": 33.51111, "lon": 126.49278, "x": 240, "y": 110},
    "seongsan": {"lat": 33.458528, "lon": 126.94225, "x": 1070, "y": 270}
}

def geo_to_pixel(lat, lon, ref1, ref2):
    x = ref1["x"] + (lon - ref1["lon"]) / (ref2["lon"] - ref1["lon"]) * (ref2["x"] - ref1["x"])
    y = ref1["y"] + (lat - ref1["lat"]) / (ref2["lat"] - ref1["lat"]) * (ref2["y"] - ref1["y"])
    return x, y

# 카테고리별 핀 색상 지정
category_colors = {
    "테마파크": "#7E318E",
    "체험": "#E50A84",
    "카페로컬": "#F39800",
    "공연": "#00AEC4"
}

st.title("🎯 제주 시설 지도 핀 자동화 도구")

# 지도 배경 이미지 업로드
bg_img_file = st.file_uploader("🖼️ 제주 지도 배경 이미지 업로드 (PNG)", type=["png"])
bg_img = None
if bg_img_file:
    bg_img = Image.open(bg_img_file)
    st.image(bg_img, caption="업로드된 지도 이미지", use_column_width=True)
else:
    st.warning("지도 이미지를 업로드해야 핀 시각화가 가능합니다.")

# 시설 엑셀 업로드
uploaded_file = st.file_uploader("📂 시설 정보 엑셀 업로드 (.xlsx, 'name', 'lat', 'lon', 'category' 포함)", type="xlsx")

if uploaded_file and bg_img:
    df = pd.read_excel(uploaded_file)
    required_cols = {"name", "lat", "lon", "category"}

    if not required_cols.issubset(df.columns):
        st.error("❗ 'name', 'lat', 'lon', 'category' 컬럼이 포함된 파일을 업로드해주세요.")
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(bg_img)

        for _, row in df.iterrows():
            color = category_colors.get(row["category"], "gray")
            try:
                x, y = geo_to_pixel(row["lat"], row["lon"], geo_refs["airport"], geo_refs["seongsan"])
                ax.plot(x, y, 'o', color=color, markersize=10)
                ax.text(x + 10, y, row["name"], fontsize=9, va='center', color='black')
            except Exception as e:
                print(f"좌표 계산 오류: {e}")
                continue

        ax.axis('off')
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="📥 결과 이미지 다운로드",
            data=buf.getvalue(),
            file_name="jeju_map_result.png",
            mime="image/png"
        )
