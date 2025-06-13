from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from services.predictor import predict_calories
from services.recommendation_system import generate_meal_plan
import shutil
import uuid
from pathlib import Path
import json
from pydantic import BaseModel # <-- Tambahkan import ini

# Definisikan model data untuk endpoint POST
class TestItem(BaseModel):
    name: str
    value: int

app = FastAPI(
    title="CaloTrack API",
    description="API untuk prediksi kalori dari gambar makanan dan rekomendasi makanan.",
    version="1.0.0"
)

# CORS: supaya frontend bisa akses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("temp_uploads") # <-- Disederhanakan untuk Azure
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --- Endpoint Pengujian ---

@app.get("/test-get", tags=["Testing"])
async def test_get():
    """
    Endpoint GET sederhana untuk memverifikasi bahwa server berjalan.
    """
    return {"status": "ok", "message": "GET request successful!"}

@app.post("/test-post", tags=["Testing"])
async def test_post(item: TestItem):
    """
    Endpoint POST sederhana untuk memverifikasi penerimaan data.
    """
    return {"status": "received", "data": item}

# --- Endpoint Aplikasi Utama ---

@app.post("/predict-image", tags=["Prediction"])
async def predict_image(file: UploadFile = File(...)):
    file_ext = file.filename.split('.')[-1]
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.{file_ext}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = predict_calories(str(file_path))
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        file_path.unlink(missing_ok=True)

@app.post("/recommendation", tags=["Recommendation"])
async def recommend_meal(calorie_goal: int = Form(...)):
    try:
        result = generate_meal_plan(calorie_goal)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/recommend", tags=["Recommendation"])
async def recommend(calories: int = Query(..., ge=1)):
    return generate_meal_plan(calories)

@app.get("/articles", tags=["Articles"])
def get_articles():
    try:
        # Menggunakan path relatif yang aman
        file_path = Path(__file__).parent / "data" / "articles.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"articles": data}
    except Exception as e:
        return {"error": str(e)}