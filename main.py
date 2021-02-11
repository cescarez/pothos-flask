from flask import Flask, request, Response, abort, jsonify
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
            'full_name': submitted_data['full_name'],
            'phone_number': submitted_data['phone_number'],
            'address': {
                'street': submitted_data['address']['street'],
                'city': submitted_data['address']['city'],
                'state': submitted_data['address']['state'],
                'postal_code': submitted_data['address']['postal_code'],
            },
            'avatar_url': submitted_data['avatar_url'],
            'price_rate': {
                'water_by_plant': float(submitted_data['price_rate']['water_by_plant']) if submitted_data['price_rate']['water_by_plant'] else '',
                'water_by_time': float(submitted_data['price_rate']['water_by_time'])  if submitted_data['price_rate']['water_by_time'] else '',
                'repot_by_plant': float(submitted_data['price_rate']['repot_by_plant']) if submitted_data['price_rate']['repot_by_plant'] else '',
                'repot_by_time': float(submitted_data['price_rate']['repot_by_time']) if submitted_data['price_rate']['repot_by_time'] else ''
            }
        }
        db.child('users').push(new_user)

        return(new_user, 201)
    else:
        return({'message':'Invalid endpoint. User profile was not saved to the database.'}, 404)

#sitters and owners indexes
@app.route('/<string:usertype>', methods=['GET'])
def users_index(usertype):
    db = firebase.database()
    if (usertype == 'sitters' or usertype == 'owners'):
        if usertype == 'sitters':
            users = db.child('users').order_by_child('sitter').equal_to(True).get().val()
        else:
            users = db.child('users').order_by_child('owner').equal_to(True).get().val()
        if users:
            return(users)
        else:
            return({'message': 'No {usertype} in database to display.'}, 204)
    else:
        return({'message':'Invalid endpoint.'}, 404)


#user show via backend ID
@app.route('/users/<string:id>', methods=['GET', 'PUT'])
def users_show(id):
    db = firebase.database()
    if request.method == 'GET':
        user = db.child('users').child(escape(id)).get().val()
        if user:
            return(user)
        else:
            return({'message': 'No user profile has been stored with the entered user ID.'}, 404)
    else:
        submitted_data = request.get_json()
        user = db.child('users').child(escape(id)).get().val()
        if user:
            updated_user = {
                'sitter': submitted_data['sitter'],
                'owner': submitted_data['owner'],
                'bio': submitted_data['bio'],
                'full_name': submitted_data['full_name'],
                'phone_number': submitted_data['phone_number'],
                'address': {
                    'street': submitted_data['address']['street'],
                    'city': submitted_data['address']['city'],
                    'state': submitted_data['address']['state'],
                    'postal_code': submitted_data['address']['postal_code'],
                },
                'price_rate': {
                    'water_by_plant': float(submitted_data['price_rate']['water_by_plant']) if submitted_data['price_rate']['water_by_plant'] else '',
                    'water_by_time': float(submitted_data['price_rate']['water_by_time'])  if submitted_data['price_rate']['water_by_time'] else '',
                    'repot_by_plant': float(submitted_data['price_rate']['repot_by_plant']) if submitted_data['price_rate']['repot_by_plant'] else '',
                    'repot_by_time': float(submitted_data['price_rate']['repot_by_time']) if submitted_data['price_rate']['repot_by_time'] else ''
                }
            }
            db.child('users').child(escape(id)).update(updated_user)
            return(updated_user, 200)
        else:
            return({'message':'No user profile has been stored with the entered user ID.'}, 404)

#user show via frontend ID
@app.route('/users/current/<string:auth_id>', methods=['GET'])
def find_user(auth_id):
    db = firebase.database()
    user = db.child('users').order_by_child('auth_id').equal_to(auth_id).get().val()
    if user:
        return(user, 200)
    else:
        return({'message':'No user profile has been saved with the logged in user\'s authentication ID.'}, 404)


#sitting request post
@app.route('/requests', methods=['POST'])
def submit_request():
    db = firebase.database()
    #assumes JSON format, not form 
    submitted_data = request.get_json()
    new_request = {
        'time_requested': str(datetime.utcnow()),
        'time_confirmed': '',
        'owner': submitted_data['owner'],
        'sitter': submitted_data['sitter'],
        'status': 'pending',
        'date_of_service': submitted_data.get('date_of_service'),
        'services': {
            'water_by_plant': submitted_data['services']['water_by_plant'],
            'water_by_time': submitted_data['services']['water_by_time'],
            'repot_by_plant': submitted_data['services']['repot_by_plant'],
            'repot_by_time': submitted_data['services']['repot_by_time'],
        },
        'owner_rating': '',
        'sitter_rating': '',
    }
    postedRequest = db.child('requests').push(new_request)
    # print(postedRequest['name']) #this is the newly pushed/generated request ID
    start_chat(postedRequest['name'], new_request)

    return({'message':'Request was successfully submitted'},201)
#first message that initializes chat, sent with request
def start_chat(request_id, request):
    db = firebase.database()
    #for string interpolation and more descriptive request messaging.... to be implemented... not now.
    watering_count = request['services']['water_by_plant']
    watering_hours = int(request['services']['water_by_time']) * 0.5
    repotting_count = request['services']['repot_by_plant']
    repotting_hours = int(request['services']['repot_by_time']) * 0.5
    watering = watering_count or watering_hours
    repotting = repotting_count or repotting_hours

    if (watering and repotting):
        message = 'Hey bud (pun intended), are you available for watering and plant sitting services?'
    elif(watering):
        message = 'Hey bud (pun intended), are you available for watering services?'
    elif (repotting):
        message = 'Hey bud (pun intended), are you available for repotting services?'
    else:
        message = 'Hey bud (pun intended), just sayin\' hi :).'

    new_message = {
        'timestamp': str(datetime.utcnow()),
        'message': message,
        'sender': request['owner'],
        'request_id': request_id 
    }
    db.child('messages').push(new_message)
    return({'message':'Message successfully sent'})

#request show via backend ID
@app.route('/requests/<string:id>', methods=['GET', 'PUT'])
def request_show(id):
    db = firebase.database()
    if request.method == 'GET':
        sitting_request = db.child('requests').child(escape(id)).get().val()
        if sitting_request:
            return(sitting_request, 200)
        else:
            return({'message': 'No request has been made with this ID'}, 204)
    else:
        submitted_data = request.get_json()
        sitting_request = db.child('requests').child(escape(id)).get().val()
        if sitting_request:
            confirm_request = {
                'time_confirmed': str(datetime.utcnow()),
                'status': submitted_data['status'],
            }
            db.child('requests').child(escape(id)).update(confirm_request)
            return(confirm_request, 200) #success message needed
        else:
            return({'message':'No request has been made with this ID.'}, 204)

@app.route('/requests-by-sitter/<string:id>', methods=['GET'])
def find_requests(id):
    db = firebase.database()
    request = db.child('requests').order_by_child('sitter').equal_to(id).get().val()
    if request:
        for request_id, request_data in request.items():
            owner = db.child('users').child(escape(request_data['owner'])).get().val()
            sitter = db.child('users').child(escape(request_data['sitter'])).get().val()
            request[request_id]['owner_name'] = owner['full_name']
            request[request_id]['sitter_name'] = sitter['full_name']
        return(request, 200)
    else:
        return({'message': 'No requests have been saved with the logged in user\'s ID.'}, 204)

@app.route('/requests-by-user/<string:id>', methods=['GET'])
def user_requests(id):
    db = firebase.database()
    request = db.child('requests').order_by_child('owner').equal_to(id).get().val()
    if request:
        request.update(db.child('requests').order_by_child('sitter').equal_to(id).get().val())
    else:
        request = db.child('requests').order_by_child('sitter').equal_to(id).get().val()
        request.update(db.child('requests').order_by_child('owner').equal_to(id).get().val())
    if request:
        for request_id, request_data in request.items():
            owner = db.child('users').child(escape(request_data['owner'])).get().val()
            sitter = db.child('users').child(escape(request_data['sitter'])).get().val()
            request[request_id]['owner_name'] = owner['full_name']
            request[request_id]['sitter_name'] = sitter['full_name']
        return(request, 200)
    else:
        return({'message': 'No requests have been saved with the logged in user\'s ID.'}, 204)

#chat messages post
@app.route('/messages', methods=['POST'])
def send_message():
    db = firebase.database()
    #assumes JSON format, not form 
    submitted_data = request.get_json()
    new_message = {
        'timestamp': str(datetime.utcnow()),
        'message': submitted_data['message'],
        'sender': submitted_data.get('sender'),
        'request_id': submitted_data['request_id'],
        'photo': submitted_data['photo'],
        'photo_url': submitted_data['photo_url']
    }
    db.child('messages').push(new_message)
    return({'message':'Message successfully sent'}, 200)

@app.route('/messages-by-request/<string:id>', methods=['GET'])
def find_messages(id):
    db = firebase.database()
    message_list = db.child('messages').order_by_child('request_id').equal_to(id).get().val()
    if message_list:
        for message_id, message_data in message_list.items():
            user = db.child('users').child(escape(message_data['sender'])).get().val()
            message_list[message_id]['sender_name'] = user['full_name']
        return(message_list, 200)
    else:
        return({'message': 'No messages have been saved with the request ID.'}, 204)

@app.route('/photos', methods=['POST'])
def upload_photos():
    db = firebase.database()
    #assumes JSON format, not form 
    submitted_data = request.get_json()
    new_photo = {
        'timestamp': str(datetime.utcnow()),
        'photo_url': submitted_data['photo_url'],
        'sender': submitted_data['sender'],
        'request_id': submitted_data['request_id']
    }
    db.child('photos').push(new_photo)
    return({'message':'Photo successfully saved'}, 200)

@app.route('/photos-by-request/<string:id>', methods=['GET'])
def find_photos(id):
    db = firebase.database()
    photo_list = db.child('photos').order_by_child('request_id').equal_to(id).get().val()
    if photo_list:
        return(photo_list, 200)
    else:
        return({'message': 'No photos have been saved with the request ID.'}, 204)


if __name__ == '__main__':
    print('This file has been run as main')
else:
    print('This file has been imported as a module.')