FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
COPY app.py / 
COPY functions.py /
COPY requirements.txt / 
RUN pip install -r requirements.txt
RUN playwright install
CMD ["gunicorn", "app:app"]