from flask import Flask, request, Response, abort
from flask_cors import CORS, cross_origin
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
CORS(app, support_credentials=True)
firebase = pyrebase.initialize_app(config)

#user post
@app.route('/users', methods=['POST'])
def add_user():
    db = firebase.database()
    if request.method == 'POST':
        #assumes JSON format, not form 
        submitted_data = request.get_json()
        new_user = {
            'auth_id': submitted_data['auth_id'],
            'date_joined': str(datetime.utcnow()),
            'sitter': submitted_data['sitter'],
            'owner': submitted_data['owner'],
            'bio': submitted_data['bio'],
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
            'chat_history': {},
            'price_rate': {
                'water_by_plant': float(submitted_data['price_rate']['water_by_plant']) if submitted_data['price_rate']['water_by_plant'] else '',
                'water_by_time': float(submitted_data['price_rate']['water_by_time'])  if submitted_data['price_rate']['water_by_time'] else '',
                'repot_by_plant': float(submitted_data['price_rate']['repot_by_plant']) if submitted_data['price_rate']['repot_by_plant'] else '',
                'repot_by_time': float(submitted_data['price_rate']['repot_by_time']) if submitted_data['price_rate']['repot_by_time'] else ''
            }
        }
        db.child('users').push(new_user)
        return(Response(
            "{'message':'User profile was successfully added to the database. Check database for posted data.'}",
            status=200,
            mimetype='application/json'
        ))
    else:
        return(Response(
            "{'error':'Invalid endpoint. User profile was not saved to the database.'}",
            status=404,
            mimetype='application/json'
        ))

#sitters and owners indexes
@app.route('/<string:usertype>', methods=['GET'])
def users_index(usertype):
    #does db order change when a patch request is sent? if so, then chain a .order_by_key() as first call
    usertype = escape(usertype)[0:-1]
    db = firebase.database()
    if (usertype == 'sitter' or usertype == 'owner'):
        if usertype == 'sitter':
            users = db.child('users').order_by_child('sitter').equal_to(True).get().val()
        else:
            users = db.child('users').order_by_child('sitter').equal_to(True).get().val()
        if users:
            return(users)
        else:
            return({'message': 'No {usertype} in database to display.'})
    else:
        return(Response("{'error':'Invalid endpoint.'}", status=404, mimetype='application/json'))

#user show via backend ID
@app.route('/users/<string:id>', methods=['GET', 'PATCH'])
def users_show(id):
    db = firebase.database()
    if request.method == 'GET':
        user = db.child('users').child(escape(id)).get().val()
        if user:
            return(user)
        else:
            return({'message': 'No user profile has been stored with the entered user ID.'})
    else:
        submitted_data = request.get_json()
        user = db.child('users').child(escape(id)).get().val()
        if user:
            updated_user = {
                'sitter': submitted_data['sitter'],
                'owner': submitted_data['owner'],
                'bio': submitted_data['bio'],
                'username': submitted_data['username'],
                'full_name': submitted_data['full_name'],
                'phone_number': submitted_data['phone_number'],
                'address': {
                    'street': submitted_data['address']['street'],
                    'city': submitted_data['address']['city'],
                    'state': submitted_data['address']['state'],
                    'postal_code': submitted_data['address']['postal_code'],
                    'country': submitted_data['address']['country']
                },
                'avatar_url': submitted_data['avatar_url'],
                'price_rate': {
                    'water_by_plant': float(submitted_data['price_rate']['water_by_plant']) if submitted_data['price_rate']['water_by_plant'] else '',
                    'water_by_time': float(submitted_data['price_rate']['water_by_time'])  if submitted_data['price_rate']['water_by_time'] else '',
                    'repot_by_plant': float(submitted_data['price_rate']['repot_by_plant']) if submitted_data['price_rate']['repot_by_plant'] else '',
                    'repot_by_time': float(submitted_data['price_rate']['repot_by_time']) if submitted_data['price_rate']['repot_by_time'] else ''
                }
            }
            db.child('users').child(escape(id)).update(updated_user)
            return(updated_user)
        else:
            abort(404, 'No user profile has been stored with the entered user ID.')
        


#user show via frontend ID
@app.route('/users/current/<string:auth_id>', methods=['GET'])
def find_user(auth_id):
    db = firebase.database()
    user = db.child('users').order_by_child('auth_id').equal_to(auth_id).get().val()
    if user:
        return(user)
    else:
        return({'message': 'No user profile has been saved with the logged in user\'s authentication ID.'})


if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('This file has been imported as a module.')