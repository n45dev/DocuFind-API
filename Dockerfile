FROM python:3.9-slim

WORKDIR /app

COPY ./api.py /app/api.py
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN mkdir -p /app/data
# Initialize the database
RUN python -c "from api import init_db; init_db()"

EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
