from flask import Flask

app = Flask(__name__)

# Set the secret key to a random value (ensure it's unique and secure for production)
app.secret_key = 'your_super_secret_key'

# Import routes after app initialization to avoid circular imports
from app import routes
