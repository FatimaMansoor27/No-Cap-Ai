# No Cap Ai

Secure, private ChatGPT-like interface using Python and Flask

## Features
- White clean modern theme
- Persistent chat history (SQLite)
- Left sidebar: New Chat, History, Search
- Responsive (mobile-friendly)
- Memory across sessions
- Delete chat option
- Voice Input (speech to text)

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite + SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI**: Groq API (Llama 3.3)
- **Voice**: Browser Speech Recognition API


## Setup
1. `pip install -r requirements.txt`
2. Add XAI_API_KEY to .env
3. `python app.py`
