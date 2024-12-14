from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, send
import requests

from utils import generate_room_code, aiLib, delete_connection, new_connection, info
from utils import *

init(autoreset=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SDKFJSDFOWEIOF'
socketio = SocketIO(app)

rooms = {}

@app.route('/v1', methods=['GET', 'POST'])
def api():
    if request.method == 'GET':
        return redirect(url_for('home'))
    if request.method == 'POST':
        try:
            room=request.json["room"]
            rooms.pop(room)
        except KeyError: return {'error': 'Room not found'}



@app.route('/', methods=["GET", "POST"])
def home():
    session.clear()

    if request.method == "POST":
        name = request.form.get('name')
        create = request.form.get('create', False)

        if not name:
            return render_template('home.html', error="Name is required")

        if name=='AIBot':
            return render_template('home.html', error="You cant have that name.")
        
        if create != False:
            room_code = generate_room_code(6, list(rooms.keys()))
            new_room = {
                'members': 0,
                'messages': []
            }
            rooms[room_code] = new_room

        session['room'] = room_code
        session['name'] = name
        return redirect(url_for('room'))
    else:
        return render_template('home.html')


@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')

    if name is None or room is None or room not in rooms:
        return redirect(url_for('home'))

    messages = rooms[room]['messages']
    return render_template('room.html', room=room, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    name = session.get('name')
    room = session.get('room')
    if name is None or room is None:
        return
    if room not in rooms:
        leave_room(room)
    
    try:
        join_room(room)
        send({
            "sender": "",
            "message": f"Welcome! The bot may take some time to generate a response depending on the length of the prompt."
        }, to=room)
        rooms[room]["members"] += 1
        new_connection("New Connection established. Room: {0}".format(room))
        info("Rooms: {0}".format(rooms.keys()))
    except KeyError:
        return redirect(url_for("home"))


@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')

    if room not in rooms:
        return

    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    send({
        "sender": "",
        "message": "AIBot is thinking"
    }, to = room)
    send({
        "sender": "AIBot",
        "message":aiLib.generate_content(str(payload['message'])+' in about 60 words.').text
    }, to = room)
    rooms[room]["messages"].append(message)

@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
            delete_connection('Room deletion: {0}'.format(room))
            info("Rooms: {0}".format(rooms.keys()))


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
