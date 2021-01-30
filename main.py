from flask import Flask
from pyrebase import pyrebase
import pyrebase
import os
from dotenv import load_dotenv
load_dotenv()

config = {
  'apiKey': os.getenv('FLASK_APP_FIREBASE_API_KEY'),
  'authDomain': os.getenv('FLASK_APP_FIREBASE_AUTH_DOMAIN'),
  'databaseURL': os.getenv('FLASK_APP_FIREBASE_DATABASE_URL'),
  'storageBucket': os.getenv('FLASK_APP_FIREBASE_STORAGE_BUCKET'),
#   'serviceAccount': os.getenv('')
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(config)

@app.route('/hello', methods=["GET"])
def hello():
    return ({'message':'hello world'})

if __name__ == '__main__':
    app.run(debug=True)