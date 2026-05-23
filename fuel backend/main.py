import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Твоя ссылка Supabase
DATABASE_URL = "postgresql://postgres:Popa101za1!@db.suvefdfxmijlqnyggflj.supabase.co:6543/postgres"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Авто-создание таблиц при старте
@app.on_event("startup")
def startup_event():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS pwa_cars (name TEXT PRIMARY KEY, color TEXT, visible BOOLEAN, deleted BOOLEAN)")
        cur.execute("CREATE TABLE IF NOT EXISTS pwa_refuels (id SERIAL PRIMARY KEY, car TEXT, octane TEXT, date TEXT, price REAL, liters REAL, odometer TEXT, distance REAL)")
        conn.commit()
        cur.close()
        conn.close()
        print("БД готова!")
    except Exception as e:
        print(f"Ошибка БД: {e}")

# Модели данных
class CarItem(BaseModel):
    name: str
    color: str
    visible: bool
    deleted: bool

class RefuelItem(BaseModel):
    car: str
    octane: str
    date: str
    price: float
    liters: float
    odometer: str
    distance: Optional[float] = None

# --- API ---
@app.get("/api/cars", response_model=List[CarItem])
def get_cars():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT name, color, visible, deleted FROM pwa_cars")
            return cur.fetchall()

@app.post("/api/cars")
def save_cars(cars: List[CarItem]):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pwa_cars")
            for car in cars:
                cur.execute(
                    "INSERT INTO pwa_cars (name, color, visible, deleted) VALUES (%s, %s, %s, %s)",
                    (car.name, car.color, car.visible, car.deleted)
                )
            conn.commit()
    return {"status": "ok"}

@app.get("/api/refuels", response_model=List[RefuelItem])
def get_refuels():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT car, octane, date, price, liters, odometer, distance FROM pwa_refuels")
            return cur.fetchall()

@app.post("/api/refuels")
def save_refuels(refuels: List[RefuelItem]):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pwa_refuels")
            for r in refuels:
                cur.execute(
                    "INSERT INTO pwa_refuels (car, octane, date, price, liters, odometer, distance) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (r.car, r.octane, r.date, r.price, r.liters, r.odometer, r.distance)
                )
            conn.commit()
    return {"status": "ok"}
