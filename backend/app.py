from flask import Flask
from routes import register_routes

app = Flask(__name__)
register_routes(app)
app.run(host='0.0.0.0', port=8000)
