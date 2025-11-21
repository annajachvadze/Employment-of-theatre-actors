import streamlit as st
import requests
import base64
from PIL import Image
import io

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.error("⚠️ Библиотека streamlit-drawable-canvas не установлена!")
    st.code("pip install streamlit-drawable-canvas")

st.set_page_config(
    page_title="Распознавание рукописных цифр",
    page_icon="🔢",
    layout="centered"
)

st.title("🔢 Распознавание рукописных цифр")

if not CANVAS_AVAILABLE:
    st.stop()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎨 Нарисуйте цифру")

    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 1)",
        stroke_width=20,
        stroke_color="rgba(255, 255, 255, 1)",
        background_color="rgba(0, 0, 0, 1)",
        width=280,
        height=280,
        drawing_mode="freedraw",
        key="canvas",
        update_streamlit=True,
    )

    predict_clicked = st.button("🔍 Распознать", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Результат")

    if predict_clicked:
        if canvas_result.image_data is not None:
            with st.spinner("Распознавание..."):
                try:
                    image_data = canvas_result.image_data

                    if image_data.shape[2] == 4:
                        rgb_data = image_data[:, :, :3]
                    else:
                        rgb_data = image_data

                    pil_image = Image.fromarray(rgb_data.astype('uint8'))

                    buffered = io.BytesIO()
                    pil_image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    # Правильный запрос к серверу
                    response = requests.post(
                        "http://localhost:8000/predict",  # Порт изменен на 8000
                        json={"image_data": f"data:image/png;base64,{img_str}"},
                        timeout=10
                    )

                    if response.status_code == 200:
                        result = response.json()
                        predicted_digit = result['predicted_digit']
                        confidence = result['confidence']

                        st.success(f"**Распознанная цифра: {predicted_digit}**")
                        st.info(f"**Уверенность: {confidence:.2%}**")

                        st.subheader("Вероятности всех цифр:")
                        probabilities = result['probabilities']

                        for digit, prob in sorted(probabilities.items(), key=lambda x: -x[1]):
                            if prob > 0.001:
                                st.write(f"Цифра {digit}: {prob:.2%}")
                                st.progress(float(prob))

                    else:
                        st.error(f"Ошибка сервера: {response.status_code} - {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("Не удалось подключиться к серверу. Запустите server.py")
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Пожалуйста, нарисуйте цифру перед распознаванием")