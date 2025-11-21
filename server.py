from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from PIL import Image
import io
import base64
import tensorflow as tf
from tensorflow import keras

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.SGD(),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

try:
    model.load_weights('model.weights.h5')
    print("Веса модели успешно загружены")
except Exception as e:
    print(f"Ошибка загрузки весов: {e}")

class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class ImageData(BaseModel):
    image_data: str

def preprocess_image(image_data):
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('L')

        image = image.resize((28, 28))
        image_array = np.array(image)

        image_array = image_array.astype('float32') / 255.0

        if np.mean(image_array) > 0.5:
            image_array = 1.0 - image_array

        return image_array.reshape(1, 28, 28)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обработки изображения: {e}")

@app.post("/predict")
async def predict_digit(item: ImageData):
    try:
        processed_image = preprocess_image(item.image_data)

        predictions = model.predict(processed_image)
        predicted_digit = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_digit])

        probabilities = {
            str(i): float(prob) for i, prob in enumerate(predictions[0])
        }

        return {
            'predicted_digit': int(predicted_digit),
            'confidence': confidence,
            'probabilities': probabilities,
            'class_name': class_names[predicted_digit]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Сервер распознавания цифр работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)