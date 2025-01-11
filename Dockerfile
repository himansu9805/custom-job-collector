FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY custom_job_collector ./custom_job_collector
COPY linkedin_cookies.json ./linkedin_cookies.json

CMD ["python", "-m", "custom_job_collector.main"]