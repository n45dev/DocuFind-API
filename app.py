from flask import Flask
from flask_cors import CORS
from config import API_KEY
from db import init_db
from routes import register_routes

app = Flask(__name__)
CORS(app)

# Initialize the MySQL database
init_db()

# Register routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
