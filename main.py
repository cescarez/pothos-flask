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

@app.route('/<string:usertype>', methods=['GET', 'POST'])
def users_index(usertype):
    db = firebase.database()
    usertype = escape(usertype)
    if request.method == 'POST':
        submitted_data = request.get_json()
        if (usertype == 'sitters' or usertype == 'owners'):
            new_user = {
                'date_joined': str(datetime.utcnow()),
                'name': submitted_data['name'],
                'email': submitted_data['email'],
                'phone': submitted_data['phone']
            }
        db.child(usertype).push(new_user)
        return({'message':'test data successfully posted. check database for posted data'})
    else:
        users = db.child(usertype).get().val()
        return(users)

@app.route('/<string:usertype>/<string:id>', methods=['GET'])
def users_show(usertype, id):
    db = firebase.database()
    usertype = escape(usertype)
    if (usertype == 'sitters' or usertype == 'owners'):
        sitter = db.child(usertype).child(escape(id)).get().val()
    return(sitter)



if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('Error, this file should not be imported as a module.')