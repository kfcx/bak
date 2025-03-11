FROM python:3.9-slim
LABEL maintainer="Naihe"
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PROJECT_ENV prod

#CMD ["gunicorn", "-c", "./deploy/gunicorn.conf.py"]
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
