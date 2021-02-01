from flask import Flask, request
import os
from datetime import datetime
from markupsafe import escape
from pyrebase import pyrebase
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
        #assumes JSON format, not form 
        submitted_data = request.get_json()
        if (usertype == 'sitters' or usertype == 'owners'):
            new_user = {
                'date_joined': str(datetime.utcnow()),
                'type': {
                    #how will this be passed from front end?
                    'sitter': eval(usertype == 'sitters'),
                    'owner': eval(usertype == 'owners')
                },
                'username': submitted_data['username'],
                'full_name': submitted_data['full_name'],
                'phone_number': submitted_data['phone_number'],
                'email': submitted_data['email'],
                'address': {
                    'street': submitted_data['address']['street'],
                    'city': submitted_data['address']['city'],
                    'state': submitted_data['address']['state'],
                    'postal_code': submitted_data['address']['postal_code'],
                    'country': submitted_data['address']['country']
                },
                'avatar_url': submitted_data['avatar_url'],
                # 'rating': submitted_data['rating'],
                'messages': {},
                'price_rate': {
                    'water_by_plant': submitted_data['price_rate']['water_by_plant'],
                    'water_by_time': submitted_data['price_rate']['water_by_time'],
                    'repot_by_plant': submitted_data['price_rate']['repot_by_plant'],
                    'repot_by_time': submitted_data['price_rate']['repot_by_time'],
                }
            }
            
            db.child('users').push(new_user)
            return({'message':'new user successfully added. check database for posted data'})
        else:
            return({'message':'invalid endpoint. No user created.'})
    else:
        #review this logic
        #does db order change when a patch request is sent? if so, then chain a .order_by_key() as first call
        users = db.child('users').order_by_child('type').order_by_child.(usertype[0:-1]).equal_to(True).get().val()
        return(users)

@app.route('/<string:usertype>/<string:id>', methods=['GET'])
def users_show(usertype, id):
    db = firebase.database()
    usertype = escape(usertype)
    if (usertype == 'sitters' or usertype == 'owners'):
        user = db.child(usertype).child(escape(id)).get().val()
    return(user)



if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('This file has been imported as a module.')