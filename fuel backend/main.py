import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Правильная настройка CORS — разрешаем фронтенду слать данные
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Твоя ссылка на базу Supabase
DATABASE_URL = "postgresql://postgres:Popa101za1!@db.suvefdfxmijlqnyggflj.supabase.co:6543/postgres"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Инициализация таблиц в облаке
try:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Таблица машин
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pwa_cars (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL,
                    visible BOOLEAN DEFAULT TRUE,
                    deleted BOOLEAN DEFAULT FALSE
                )
            """)
            # Таблица заправок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pwa_refuels (
                    id SERIAL PRIMARY KEY,
                    car TEXT NOT NULL,
                    octane TEXT NOT NULL,
                    date TEXT NOT NULL,
                    price REAL NOT NULL,
                    liters REAL NOT NULL,
                    odometer TEXT NOT NULL,
                    distance REAL
                )
            """)
            conn.commit()
    print("База данных PostgreSQL успешно инициализирована!")
except Exception as e:
    print("Ошибка инициализации БД:", e)

# Модели данных для проверки запросов
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

# --- API ЭНДПОИНТЫ ДЛЯ МАШИН ---
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

# --- API ЭНДПОИНТЫ ДЛЯ ЗАПРАВОК ---
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
