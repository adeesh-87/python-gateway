from flask import *
from flask_socketio import SocketIO, emit
from random import random
from time import sleep
from threading import Thread, Event
#import coord_interface.py

__author__ = 'Adeesh'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True

#devDataThread = Thread()

#class RandomThread(Thread):
#    def __init__(self):
#        print("Starting Serial Reading")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/serial")
def serial_test():
    return render_template('serial_test.html')
#@socketio.on('connect', namespace='/test')
#def connect():
    

if __name__ == "__main__":
    #socketio.run(app)
    app.run()
