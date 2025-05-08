# 제주 지도 자동 핀 시각화 도구 (엑셀 + PNG 이미지 기반 + 가독성 개선 + 웹폰트 적용)

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import streamlit as st
import matplotlib.patheffects as path_effects
import matplotlib.font_manager as fm
import os

st.set_page_config(layout="wide")

# 웹폰트 등록 (S-CoreDream-7Bold)
font_url = "https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/S-CoreDream-7Bold.woff"
font_path = "/tmp/S-CoreDream-7Bold.woff"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f:
        f.write(requests.get(font_url).content)

fm.fontManager.addfont(font_path)
custom_font = fm.FontProperties(fname=font_path)

st.title("📍 제주 지도 자동 핀 시각화 도구")

# 지도 이미지 업로드
map_img_file = st.file_uploader("🖼️ 제주 지도 이미지 업로드 (PNG)", type=["png"])

# 엑셀 업로드
data_file = st.file_uploader("📂 시설 좌표 엑셀 업로드 (.xlsx, 'name', 'x', 'y', 'color', '번호' 포함)", type=["xlsx"])

if map_img_file and data_file:
    # 지도 열기
    map_img = Image.open(map_img_file)
    df = pd.read_excel(data_file)

    # 시각화 시작
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(map_img)

    # 핀 및 텍스트 표시
    for _, row in df.iterrows():
        x, y = row['x'], row['y']
        color = row['color']
        번호 = row['번호']
        label = row['name']

        # 마커 (원형 + 번호)
        ax.plot(x, y, 'o', color=color, markersize=14)
        txt_number = ax.text(
            x, y, str(번호), fontsize=10, ha='center', va='center', color='white', weight='bold', fontproperties=custom_font
        )
        txt_number.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='black'),
            path_effects.Normal()
        ])

        # 이름 텍스트 - 마커 오른쪽 위로 띄워서 겹침 방지
        txt_label = ax.text(
            x + 18, y - 10, label, fontsize=11, color='black', fontproperties=custom_font
        )
        txt_label.set_path_effects([
            path_effects.Stroke(linewidth=3, foreground='white'),
            path_effects.Normal()
        ])

    ax.axis('off')
    st.pyplot(fig)

    # 이미지 다운로드용 버퍼
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button(
        label="📥 지도 이미지 다운로드",
        data=buf.getvalue(),
        file_name="jeju_map_with_pins.png",
        mime="image/png"
    )
else:
    st.info("지도 이미지와 엑셀 파일을 모두 업로드해주세요.")
