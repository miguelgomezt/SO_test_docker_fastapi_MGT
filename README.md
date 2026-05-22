## Punto 1 - Gestión de archivos en Amazon S3
### Bucket creado
`user-1025886186-ueia-so` en la región `us-east-1`
### Operaciones con AWS CLI
```bash
# Cargar archivo
aws s3 cp archivo.txt s3://user-1025886186-ueia-so/

# Verificar carga
aws s3 ls s3://user-1025886186-ueia-so/

# Descargar archivo
aws s3 cp s3://user-1025886186-ueia-so/archivo.txt ~/descargados/
```

### Operaciones con boto3
```python
import boto3
s3 = boto3.client('s3')

# Cargar
s3.upload_file('archivo.txt', 'user-1025886186-ueia-so', 'archivo.txt')
# Descargar
s3.download_file('user-1025886186-ueia-so', 'archivo.txt', 'descargado.txt')
```

---

## Punto 2 - Despliegue en Amazon EC2

### Instancia
- **Nombre:** fastapi-server
- **AMI:** Ubuntu 26.04 LTS
- **Tipo:** t3.micro
- **IP pública:** 13.219.221.192

### Pasos de configuración
```bash
# Conexion a la instancia
ssh -i fastApi-key-MGT.pem ubuntu@ec2-13-219-221-192.compute-1.amazonaws.com
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar las dependencias necesarias
sudo apt install -y python3-pip python3-venv git

# Se clona repositorio
git clone https://github.com/miguelgomezt/SO_test_docker_fastapi_MGT.git
cd SO_test_docker_fastapi_MGT

# Crear el entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias necesarias
pip install -r requirements.txt

# Correr la aplicación
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Punto 3 - Aplicación FastAPI con S3 y RDS
### Endpoints

#### POST /upload
Sube una imagen al bucket S3 organizada por usuario y registra en RDS.
- **Parámetros:** `usuario` (string), `file` (PNG/JPG)
- **Respuesta exitosa (200):** `{"message": "Imagen cargada exitosamente", "s3_path": "usuario/imagen.jpg"}`
- **Error formato inválido (415):** `{"detail": "Formato no permitido. Use PNG o JPG/JPEG."}`

#### GET /image
Consulta la imagen en RDS y retorna URL prefirmada de S3.
- **Parámetros:** `usuario` (string), `imagen` (string)
- **Respuesta exitosa (200):** `{"url": "...", "fecha_creacion": "..."}`
- **Error no encontrado (404):** `{"detail": "Usuario o imagen no encontrada."}`

### Base de datos RDS
- **Motor:** PostgreSQL
- **Instancia:** fastapi-db-mgt
- **Tabla:** images (id, usuario, s3_path, fecha_creacion)

### Docker
```bash
# Construir imagen
docker build -t fastapi-app .

### AWS Lambda
- **Función:** fastapi-lambda-mgt
- **Imagen:** fast-appi-mgt:latest (ECR)
- **URL pública:** https://duezt3vsmvgkmfspso552k3jsm0mbrsd.lambda-url.us-east-1.on.aws/
- **Docs:** https://duezt3vsmvgkmfspso552k3jsm0mbrsd.lambda-url.us-east-1.on.aws/docs