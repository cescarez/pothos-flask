from flask import Flask
# from pyrebase import pyrebase
# from . import config

app = Flask(__name__)
# firebase = pyrebase.initialize_app(config)

@app.route('/hello', methods=["GET"])
def hello():
    return ({'message':'hello'})

if __name__ == '__main__':
    app.run(debug=True)