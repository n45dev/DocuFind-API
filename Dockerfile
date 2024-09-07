FROM python:3.9-slim

WORKDIR /app

COPY ./api.py /app/api.py
COPY ./requirements.txt /app/requirements.txt
COPY ./init_db.py /app/init_db.py

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN mkdir -p /app/data


EXPOSE 5000

# Run the application with gunicorn
CMD /bin/sh -c "python init_db.py && gunicorn -w 4 -b 0.0.0.0:5000 api:app"
