FROM python:3.11-slim
WORKDIR /app

# install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . /app

ENV FLASK_APP=api.py
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

ENV PORT=5000
CMD ["bash", "-lc", "gunicorn api:app --bind 0.0.0.0:${PORT}"]
