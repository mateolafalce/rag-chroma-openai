FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use gunicorn for production-grade serving. The Flask app is in app.py and
# the Flask application instance is named `app`.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
