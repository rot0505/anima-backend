from flask import Flask
from flask_cors import CORS
from routes import events_bp
from dotenv import load_dotenv
load_dotenv()

import os
flask_env = os.environ.get('FLASK_ENV')
print(f"FLASK_ENV is set to {flask_env}") # Output: FLASK_ENV is set to development

app = Flask(__name__)
CORS(app)
app.register_blueprint(events_bp)

if __name__ == '__main__':
    app.run()