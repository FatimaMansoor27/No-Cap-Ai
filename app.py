from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
import os
from dotenv import load_dotenv
from models import db, Chat, Message
from config import Config
from datetime import datetime
import uuid

load_dotenv()

# Debug ke liye (ye lines add karo)
print("=== DEBUG ===")
print("API Key Loaded:", bool(os.getenv("GROQ_API_KEY")))
if os.getenv("GROQ_API_KEY"):
    print("Key starts with:", os.getenv("GROQ_API_KEY")[:15] + "...")
else:
    print("No API Key found in .env")
print("=============")

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Create tables on first request (new way)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    chats = Chat.query.order_by(Chat.created_at.desc()).all()
    return render_template('index.html', chats=chats)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    title = request.json.get('title', 'New Chat with No Cap Ai')
    new_chat = Chat(title=title)
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'chat_id': new_chat.id, 'title': new_chat.title})

@app.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    messages = [{'role': m.role, 'content': m.content} for m in chat.messages]
    return jsonify({'messages': messages, 'title': chat.title})

@app.route('/chat/<int:chat_id>/message', methods=['POST'])
def send_message(chat_id):
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message'}), 400

    user_msg = Message(chat_id=chat_id, role='user', content=user_message)
    db.session.add(user_msg)
    db.session.commit()

    chat = Chat.query.get(chat_id)
    history = [{'role': m.role, 'content': m.content} for m in chat.messages]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # Groq ka model
            messages=history,
            temperature=0.7,
            max_tokens=2048
        )
        assistant_reply = response.choices[0].message.content
    except Exception as e:
        assistant_reply = f"Error: {str(e)}"

    assist_msg = Message(chat_id=chat_id, role='assistant', content=assistant_reply)
    db.session.add(assist_msg)
    db.session.commit()

    if len(chat.messages) <= 2:
        chat.title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        db.session.commit()

    return jsonify({'reply': assistant_reply})

@app.route('/search', methods=['POST'])
def search_chats():
    query = request.json.get('query', '').lower()
    chats = Chat.query.filter(Chat.title.ilike(f'%{query}%')).all()
    return jsonify([{'id': c.id, 'title': c.title, 'created_at': c.created_at.isoformat()} for c in chats])

@app.route('/history')
def history():
    chats = Chat.query.order_by(Chat.created_at.desc()).all()
    return jsonify([{'id': c.id, 'title': c.title} for c in chats])

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/chat/<int:chat_id>/delete', methods=['POST'])
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    return jsonify({'success': True})