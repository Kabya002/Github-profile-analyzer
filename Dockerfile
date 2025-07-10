#Tailwind build
FROM node:18 AS tailwind_builder

WORKDIR /app

COPY frontend/package.json frontend/tailwind.config.js ./ 
COPY frontend/src ./src
COPY backend/templates ../backend/templates 

RUN npm install --legacy-peer-deps

RUN npx tailwindcss -i ./src/input.css -o ./tailwind.css --minify


#Flask App
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential curl git && rm -rf /var/lib/apt/lists/*

COPY backend/ /app/
COPY --from=tailwind_builder /app/tailwind.css /app/static/css/tailwind.css

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
