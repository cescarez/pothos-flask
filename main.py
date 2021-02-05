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
            'address': {
                'street': submitted_data['address']['street'],
                'city': submitted_data['address']['city'],
                'state': submitted_data['address']['state'],
                'postal_code': submitted_data['address']['postal_code'],
                'country': submitted_data['address']['country']
            },
            'avatar_url': submitted_data['avatar_url'],
            # 'rating': submitted_data['rating'],
            # 'chat_history': {},
            'price_rate': {
                'water_by_plant': float(submitted_data['price_rate']['water_by_plant']) if submitted_data['price_rate']['water_by_plant'] else '',
                'water_by_time': float(submitted_data['price_rate']['water_by_time'])  if submitted_data['price_rate']['water_by_time'] else '',
                'repot_by_plant': float(submitted_data['price_rate']['repot_by_plant']) if submitted_data['price_rate']['repot_by_plant'] else '',
                'repot_by_time': float(submitted_data['price_rate']['repot_by_time']) if submitted_data['price_rate']['repot_by_time'] else ''
            }
        }
        db.child('users').push(new_user)
        return(Response(
            {'message':'User profile was successfully added to the database. Check database for posted data.'},
            status=200,
            mimetype='application/json'
        ))
    else:
        abort(404, 'Invalid endpoint. User profile was not saved to the database.')

#sitters and owners indexes
@app.route('/<string:usertype>', methods=['GET'])
def users_index(usertype):
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
        abort(404, 'Invalid endpoint.')


#user show via backend ID
@app.route('/users/<string:id>', methods=['GET', 'PUT'])
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

#sitting request post
@app.route('/requests', methods=['POST'])
def submit_request():
    db = firebase.database()
    if request.method == 'POST':
        #assumes JSON format, not form 
        submitted_data = request.get_json()
        new_request = {
            'time_requested': str(datetime.utcnow()),
            'time_confirmed': '',
            'owner': submitted_data['owner'],
            'sitter': submitted_data['sitter'],
            'status': 'pending',
            'chatID': '', #how to create a chat_log at the same time?
        }
        db.child('requests').push(new_request)
        return(Response(
            {'message':'Request was successfully submitted'},
            status=200,
            mimetype='application/json'
        ))
    else:
        abort(404, 'Invalid endpoint. Request was not saved to the database.')

#user show via backend ID
@app.route('/users/<string:id>', methods=['GET', 'PUT'])
def request_show(id):
    db = firebase.database()
    if request.method == 'GET':
        sitting_request = db.child('requests').child(escape(id)).get().val()
        if sitting_request:
            return(sitting_request)
        else:
            return({'message': 'No request has been made with this ID'})
    else:
        submitted_data = request.get_json()
        sitting_request = db.child('requests').child(escape(id)).get().val()
        if sitting_request:
            confirm_request = {
                'time_confirmed': str(datetime.utcnow()),
                'status': submitted_data['status'],
            }
            db.child('requests').child(escape(id)).update(confirm_request)
            return(confirm_request)
        else:
            abort(404, 'No request has been made with this ID.')

#sitting request post
@app.route('/chats', methods=['POST'])
def start_chat():
    db = firebase.database()
    if request.method == 'POST':
        #assumes JSON format, not form 
        submitted_data = request.get_json()
        new_chat = {
            
        }
        db.child('requests').push(new_chat)
        return(Response(
            {'message':'Chat succesfully started'},
            status=200,
            mimetype='application/json'
        ))
    else:
        abort(404, 'Invalid endpoint. User profile was not saved to the database.')


if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('This file has been imported as a module.')