# Imagen base ligera con Python preinstalado (usada en EC2 / Docker local)
# FROM python:3.11-slim

# Imagen base oficial de Lambda para Python
FROM public.ecr.aws/lambda/python:3.11

# Define el directorio de trabajo dentro del contenedor (usado en EC2 / Docker local)
# WORKDIR /app

# Copia todos los archivos del proyecto al directorio /app del contenedor (usado en EC2 / Docker local)
# COPY . /app

# Copia todos los archivos del proyecto al directorio de Lambda
COPY . ${LAMBDA_TASK_ROOT}

# Instalar las dependencias
RUN pip install -r requirements.txt

# Expone el puerto 8000 (para que se pueda acceder desde el navegador)
EXPOSE 8000

# Comando para correr con uvicorn (EC2 / Docker local)
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Comando para Lambda con Mangum
CMD ["main.handler"]