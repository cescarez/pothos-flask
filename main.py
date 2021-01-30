import os
from flask import Flask
import pyrebase
from dotenv import load_dotenv
load_dotenv()

config = {
    'apiKey': os.getenv('FLASK_APP_FIREBASE_API_KEY'),
    'authDomain': os.getenv('FLASK_APP_FIREBASE_AUTH_DOMAIN'),
    # 'databaseURL': os.getenv('FLASK_APP_FIREBASE_DATABASE_URL'),
    'databaseURL': 'https://pothos-development-default-rtdb.firebaseio.com',
    'storageBucket': os.getenv('FLASK_APP_FIREBASE_STORAGE_BUCKET'),
#     'serviceAccount': os.getenv('')
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(config)

@app.route('/hello', methods=["GET"])
def hello():
    db = firebase.database()
    data = {
        'username': 'Some Test Username',
        'name': 'Test one',
        'phone_number': '12345678',
        'email': 'testone@test.test'
    }
    db.child('users').push(data)
    return({'message':'test data successfully posted. check database for posted data'})

if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('Error, this file should not be imported as a module.')