from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_sqlalchemy import SQLAlchemy
from models import db, User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chatappsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()


socketio = SocketIO(app)



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['username'] = username
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@socketio.on('join')
def handle_join(data):
    join_room(data['room'])
    send({'msg': f"{data['username']} has joined the room."}, room=data['room'])

@socketio.on('message')
def handle_message(data):
    send({'msg': f"{data['username']}: {data['msg']}"}, room=data['room'])

@socketio.on('leave')
def handle_leave(data):
    leave_room(data['room'])
    send({'msg': f"{data['username']} has left the room."}, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
