import re
import unicodedata
from flask import Flask, request
from flask_socketio import SocketIO, emit,send
import json
from uuid import uuid4

from aventura import create_session as start_session
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

sessions = {
}

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send('Connected to the server')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def get_session(uuid = None, personagem = None):
    if uuid == None:
        # create a new uuid
        uuid = str(uuid4())
    global sessions
    print(f"Session: {uuid}")
    print(f"Sessions: {sessions}")
    if uuid in list(sessions.keys()):
        return uuid
    else:
        if not personagem == None:
            sessions[uuid] = start_session(personagem)
        chat_session = sessions[uuid]
    print(f"{chat_session}")
    return uuid

class Personagem:
    def __init__(self, nome, classe):
        self._nome = nome
        # self._genero = genero
        self._classe = classe
        # self._raca = raca

    def to_dict(self):
        return {
            'nome': self._nome,
            # 'genero': self._genero,
            'classe': self._classe,
            # 'raca': self._raca
        }

def clean_history(text):
    # Remove tabulações e substituições Unicode
    text = text.replace("\\t", "")
    text = text.replace("\\n", "\n")
    text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda x: chr(int(x.group(1), 16)), text)
    
    # Remove caracteres especiais não ASCII e normaliza caracteres Unicode
    text = ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))
    
    # Remove barras verticais, hifens e espaços em excesso
    # text = re.sub(r'\|', '', text)
    # text = re.sub(r'---', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@app.post("/create_session")        
def create_gemini_session():
    # clear console
    print("\033[H\033[J")

    json_data = json.dumps(request.get_json())
    j = json.loads(json_data)
    u = Personagem(**j)
    
    chat_id = get_session(None, u)
    chat_session = sessions[chat_id]
    
    initial_history = clean_history(chat_session.history[1].parts[0].text)
    # initial_history = "\n".join([part.parts[0].text for part in chat_session.history])
    
    socketio.emit("history_updated", json.dumps({"chat_id": chat_id, "messages": initial_history}))
    return json.dumps({"chat_id": chat_id, "historia": initial_history})

@app.get("/sessions")
def get_sessions():
    return json.dumps(list(sessions.keys()))

@app.post("/chat")
def chat():
    chat_id = request.get_json()["chat_id"]
    message = request.get_json()["message"]

    print(f"Chat ID: {chat_id}")
    chat_session = sessions[get_session(chat_id)]
    chat_session.send_message(message)
    messages = []
    for part in chat_session.history:
        message = clean_history(part.parts[0].text)
        role = part.role
        messages.append({"role": role, "message": message})

    print(messages)

    socketio.emit("history_updated", json.dumps({"chat_id": chat_id, "messages": messages}))
    return json.dumps({"chat_id": chat_id})

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.post("/create_history")        
def create_history():
    chat_id = request.args.get("chat_id")
    chat_session = get_session(chat_id)
    
    socketio.emit("history_updated", json.dumps({"chat_id": chat_id, "messages": clean_history(chat_session.history)}))
    return json.dumps({"chat_id": chat_id})

@socketio.on('history_updated')
def send_updated_history():
    chat_id = request.get_json()["chat_id"]
    chat_session = sessions[get_session(chat_id)]
    emit('history_updated', chat_session.history, broadcast=True, namespace='/chat')

if __name__ == "__main__":
    print("\033[H\033[J")
    socketio.run(app)