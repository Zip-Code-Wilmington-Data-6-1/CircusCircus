from flask import Flask
from routes.messages import messages_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Register blueprint
app.register_blueprint(messages_bp)
# Register your other blueprints too...

if __name__ == '__main__':
    app.run(debug=True)