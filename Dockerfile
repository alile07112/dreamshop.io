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

CMD ["python", "api.py"]
