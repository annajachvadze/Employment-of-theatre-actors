from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from PIL import Image
import io
import tensorflow as tf
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
labels = []


@app.get("/")
async def root():
    return {"message": "API работает!", "status": "active"}


@app.get("/health")
async def health_check():
    model_status = "loaded" if model is not None else "not loaded"
    return {"status": "healthy", "model": model_status, "labels": labels}


try:
    with open('labels.txt', 'r', encoding='utf-8') as f:
        labels = [line.strip() for line in f.readlines()]
except Exception as e:
    print(f"Ошибка загрузки labels.txt: {e}")
    labels = []

try:
    if os.path.exists('model.savedmodel'):
        model = tf.saved_model.load('model.savedmodel')

    else:
        print("model.savedmodel не найден")
        model = None

except Exception as e:
    print(f"Ошибка загрузки модели: {e}")
    model = None


@app.get("/labels")
async def get_labels():
    return {"labels": labels}


def preprocess_image(image: Image.Image, target_size=(224, 224)) -> np.ndarray:
    image = image.resize(target_size)
    image_array = np.array(image)

    if len(image_array.shape) == 2:
        image_array = np.stack([image_array] * 3, axis=-1)
    elif image_array.shape[2] == 4:
        image_array = image_array[:, :, :3]

    image_array = image_array.astype(np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_array


def predict_with_saved_model(processed_image):
    signature_key = list(model.signatures.keys())[0]
    infer = model.signatures[signature_key]

    input_tensor = tf.constant(processed_image)

    predictions = infer(input_tensor)

    output_key = list(predictions.keys())[0]
    result = predictions[output_key].numpy()[0]


    return result


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Модель не загружена")

        print(f"Получен файл: {file.filename}, тип: {file.content_type}")


        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")

        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")



        processed_image = preprocess_image(image)


        confidence_scores = predict_with_saved_model(processed_image)


        num_predictions = len(confidence_scores)
        num_labels = len(labels)


        if num_predictions != num_labels:
            temp_labels = [f"Class_{i}" for i in range(num_predictions)]
            used_labels = temp_labels
        else:
            used_labels = labels

        top_indices = np.argsort(confidence_scores)[::-1][:3]
        results = []

        for idx in top_indices:
            confidence = float(confidence_scores[idx])
            class_name = used_labels[idx] if idx < len(used_labels) else f"Class_{idx}"

            results.append({
                "class": class_name,
                "confidence": confidence,
                "confidence_percent": f"{confidence * 100:.2f}%"
            })

        print(f"Предсказание завершено. Топ: {results[0]['class']} ({results[0]['confidence_percent']})")

        return {
            "success": True,
            "predictions": results,
            "top_prediction": results[0],
            "filename": file.filename,
            "total_classes": num_predictions
        }

    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)