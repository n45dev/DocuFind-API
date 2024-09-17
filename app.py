from flask import Flask
from flask_cors import CORS
from src.config import API_KEY
from src.db import init_db
from src.routes import register_routes

app = Flask(__name__)
CORS(app)

# Initialize the MySQL database
init_db()

# Register routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
