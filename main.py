from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import boto3
import psycopg2
import os
from datetime import datetime
import uuid
from mangum import Mangum

app = FastAPI()

# Configuración
BUCKET_NAME = "user-1025886186-ueia-so"
AWS_REGION = "us-east-1"

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

ALLOWED_EXTENSIONS = {"image/png", "image/jpeg", "image/jpg"}

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(100) NOT NULL,
            s3_path VARCHAR(500) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def root():
    return {"message": "Universidad EIA"}

@app.post("/upload")
async def upload_image(usuario: str, file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Formato no permitido. Use PNG o JPG/JPEG.")
    
    init_db()
    s3_key = f"{usuario}/{file.filename}"
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    s3_client.upload_fileobj(file.file, BUCKET_NAME, s3_key)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO images (usuario, s3_path) VALUES (%s, %s)",
        (usuario, s3_key)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return {"message": "Imagen cargada exitosamente", "s3_path": s3_key}

@app.get("/image")
def get_image(usuario: str, imagen: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT s3_path, fecha_creacion FROM images WHERE usuario=%s AND s3_path=%s",
        (usuario, f"{usuario}/{imagen}")
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Usuario o imagen no encontrada.")
    
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": result[0]},
        ExpiresIn=3600
    )
    
    return {"url": url, "fecha_creacion": result[1]}

handler = Mangum(app)