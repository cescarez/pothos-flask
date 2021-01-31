import os
from datetime import datetime
from flask import Flask, request
import pyrebase
from dotenv import load_dotenv
load_dotenv()

config = {
    'apiKey': os.getenv('FLASK_APP_FIREBASE_API_KEY'),
    'authDomain': os.getenv('FLASK_APP_FIREBASE_AUTH_DOMAIN'),
    'databaseURL': os.getenv('FLASK_APP_FIREBASE_DATABASE_URL'),
    'storageBucket': os.getenv('FLASK_APP_FIREBASE_STORAGE_BUCKET')
}

app = Flask(__name__)
firebase = pyrebase.initialize_app(config)

@app.route('/owners', methods=['GET', 'POST'])
def owners():
    db = firebase.database()
    if request.method == 'POST':
        req = request.get_json()
        new_owner = {
            'name': req['name'],
            'email': req['email'],
            'phone': req['phone'],
            'date_joined': str(datetime.utcnow())
        }


        db.child('owners').push(new_owner)
        return(request.form)
        # return({'message':'test data successfully posted. check database for posted data'})
    else:
        user_list = []
        return({'message': 'get request was sent'})
if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('Error, this file should not be imported as a module.')