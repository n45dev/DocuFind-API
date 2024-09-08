FROM python:3.9-slim

WORKDIR /app

COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt
COPY ./src /app/src

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN apt update && apt install -y tesseract-ocr
RUN mkdir -p /app/data

EXPOSE 5000

# Run the application with gunicorn
CMD /bin/sh -c "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
