# client.py - обновленная версия
import streamlit as st
import requests
from PIL import Image
import json

st.set_page_config(
    page_title="Прогноз изображений",
    page_icon="🖼️",
    layout="wide"
)


def main():
    st.title("🖼️ Прогноз изображений")

    with st.container():
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()

                labels_response = requests.get("http://localhost:8000/labels", timeout=5)
                if labels_response.status_code == 200:
                    labels_data = labels_response.json()
            else:
                st.error(f"❌ Сервер вернул ошибку: {response.status_code}")
                st.json(response.json())
                return
        except requests.exceptions.ConnectionError:
            st.error("""❌ Не могу подключиться к серверу. Убедитесь, что:
            - Сервер запущен на localhost:8000
            - Вы выполнили: `python serverP.py`""")
            return
        except Exception as e:
            st.error(f"❌ Ошибка подключения: {e}")
            return

    st.divider()

    classifier = ImageClassifier()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Загрузка изображения")
        uploaded_file = st.file_uploader(
            "Выберите изображение для классификации",
            type=['png', 'jpg', 'jpeg', 'bmp'],
            help="Загрузите изображение для анализа"
        )

        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Загруженное изображение", width=300)

            except Exception as e:
                st.error(f"❌ Ошибка при открытии изображения: {e}")

    with col2:
        st.subheader("📊 Результаты")

        if uploaded_file is not None:
            if st.button("🔍 Анализировать изображение", type="primary", use_container_width=True):
                with st.spinner("Обработка изображения..."):
                    try:
                        uploaded_file.seek(0)

                        files = {"file": (uploaded_file.name, uploaded_file, "image/jpeg")}

                        response = requests.post("http://localhost:8000/predict", files=files, timeout=30)


                        if response.status_code == 200:
                            result = response.json()

                            if result.get("success", False):
                                top_prediction = result.get("top_prediction", {})
                                if top_prediction:
                                    st.info(
                                        f"**🏆 Основной результат:** {top_prediction.get('class', 'Неизвестно')} - {top_prediction.get('confidence_percent', '0%')}"
                                    )

                                predictions = result.get("predictions", [])
                                if predictions:
                                    st.subheader("Все предсказания:")

                                    for i, pred in enumerate(predictions):
                                        confidence = pred.get("confidence", 0)
                                        confidence_percent = pred.get("confidence_percent", "0%")
                                        class_name = pred.get('class', 'Неизвестно')

                                        col_pred1, col_pred2 = st.columns([3, 1])
                                        with col_pred1:
                                            st.write(f"**{i + 1}. {class_name}**")
                                            st.progress(float(confidence))
                                        with col_pred2:
                                            st.write(confidence_percent)

                                        if i < len(predictions) - 1:
                                            st.write("---")
                            else:
                                st.error("❌ Сервер сообщил об ошибке в обработке")
                                st.json(result)
                        else:
                            st.error(f"❌ Ошибка сервера: {response.status_code}")
                            try:
                                error_detail = response.json()
                                st.json(error_detail)
                            except:
                                st.write(f"Текст ошибки: {response.text}")

                    except requests.exceptions.Timeout:
                        st.error("⏰ Таймаут запроса. Сервер не ответил за 30 секунд.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Ошибка соединения. Сервер недоступен.")
                    except Exception as e:
                        st.error(f"❌ Неожиданная ошибка: {e}")
                        st.write("Детали ошибки:")
                        st.exception(e)


class ImageClassifier:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def predict_image(self, image_file):
        try:
            files = {"file": image_file}
            response = requests.post(f"{self.base_url}/predict", files=files, timeout=30)
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    main()