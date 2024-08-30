from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/send_data', methods=['POST'])
def route_send_data():
    room = request.json.get('room_name')
    send_data(room)
    return {"message": f"Data sent to room: {room}"}

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    return jsonify(rooms)

def send_data(room):
    socketio.emit('response_json', f"Upload the files", room=room)

rooms = {}

@socketio.on('join')
def on_join(data):
    room = data
    join_room(room)
    rooms[request.sid] = room
    print(f'Client joined room: {room}')

@socketio.on('disconnect')
def on_disconnect():
    room = rooms.pop(request.sid, None)
    if room is not None:
        print(f'Client disconnected from room: {room}')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
