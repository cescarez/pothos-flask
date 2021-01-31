from flask import Flask, request
import os
from datetime import datetime
from markupsafe import escape
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
        submitted_data = request.get_json()
        new_owner = {
            'date_joined': str(datetime.utcnow()),
            'name': submitted_data['name'],
            'email': submitted_data['email'],
            'phone': submitted_data['phone']
        }

        db.child('owners').push(new_owner)
        return({'message':'test data successfully posted. check database for posted data'})
    else:
        owners = db.child('owners').get().val()
        return(owners)

@app.route('/sitters', methods=['GET', 'POST'])
def sitters():
    db = firebase.database()
    if request.method == 'POST':
        submitted_data = request.get_json()
        new_sitter = {
            'date_joined': str(datetime.utcnow()),
            'name': submitted_data['name'],
            'email': submitted_data['email'],
            'phone': submitted_data['phone']
        }

        db.child('sitters').push(new_sitter)
        return({'message':'test data successfully posted. check database for posted data'})
    else:
        sitters = db.child('sitters').get().val()
        return(sitters)

@app.route('/<string:usertype>/<string:id>', methods=['GET'])
def show_user(usertype, id):
    db = firebase.database()
    usertype = escape(usertype)
    if (usertype == 'sitters' or usertype == 'owners'):
        sitter = db.child(usertype).child(escape(id)).get().val()
    return(sitter)



if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('Error, this file should not be imported as a module.')