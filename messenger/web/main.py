from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime
import time
from typing import Dict
import queue

from server.main import MessengerServicer
import messenger_pb2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messenger = MessengerServicer()
active_websockets: Dict[str, WebSocket] = {}

@app.post("/v1/messages")
async def send_message(message: dict):
    msg = messenger_pb2.Message(
        sender=message["sender"],
        to=message["to"],
        content=message["content"],
        timestamp=int(time.time())
    )
    messenger.SendMessage(msg, None)
    return {"status": "ok"}

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_websockets[username] = websocket
    
    with messenger.lock:
        messenger.active_users.add(username)
        if username not in messenger.message_queues:
            messenger.message_queues[username] = queue.Queue()
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data["type"] == "message":
                msg = messenger_pb2.Message(
                    sender=username,
                    to=data["to"],
                    content=data["content"],
                    timestamp=int(time.time())
                )
                messenger.SendMessage(msg, None)
                
                if data["to"] in active_websockets:
                    try:
                        await active_websockets[data["to"]].send_json({
                            "type": "message",
                            "sender": username,
                            "content": data["content"],
                            "timestamp": msg.timestamp
                        })
                    except Exception as e:
                        print(f"Error sending to recipient: {e}")
                
                try:
                    await websocket.send_json({
                        "type": "message",
                        "sender": username,
                        "content": data["content"],
                        "timestamp": msg.timestamp
                    })
                except Exception as e:
                    print(f"Error sending confirmation: {e}")
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {username}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        with messenger.lock:
            if username in messenger.active_users:
                messenger.active_users.remove(username)
            if username in messenger.message_queues:
                del messenger.message_queues[username]
        if username in active_websockets:
            del active_websockets[username]

@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Messenger</title>
            <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
            <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
            <script src="https://unpkg.com/babel-standalone@6.26.0/babel.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .chat { border: 1px solid #ccc; border-radius: 4px; padding: 20px; margin-bottom: 20px; height: 400px; overflow-y: auto; }
                .message { margin-bottom: 10px; padding: 10px; border-radius: 4px; }
                .message.sent { background-color: #e3f2fd; margin-left: 20%; }
                .message.received { background-color: #f5f5f5; margin-right: 20%; }
                .input { display: flex; gap: 10px; }
                input, button { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
                input { flex-grow: 1; }
                button { background-color: #2196f3; color: white; border: none; cursor: pointer; }
                button:hover { background-color: #1976d2; }
            </style>
        </head>
        <body>
            <div id="root"></div>
            <script type="text/babel">
                function App() {
                    const [username, setUsername] = React.useState('');
                    const [messages, setMessages] = React.useState([]);
                    const [input, setInput] = React.useState('');
                    const [recipient, setRecipient] = React.useState('');
                    const [ws, setWs] = React.useState(null);
                    const [isConnected, setIsConnected] = React.useState(false);

                    React.useEffect(() => {
                        if (username && !ws) {
                            const websocket = new WebSocket(`ws://${window.location.host}/ws/${username}`);
                            
                            websocket.onmessage = (event) => {
                                const data = JSON.parse(event.data);
                                if (data.type === 'message') {
                                    setMessages(prev => [...prev, {
                                        sender: data.sender,
                                        content: data.content,
                                        timestamp: new Date(data.timestamp * 1000)
                                    }]);
                                }
                            };

                            websocket.onopen = () => {
                                setIsConnected(true);
                            };

                            websocket.onclose = () => {
                                setIsConnected(false);
                            };

                            setWs(websocket);

                            return () => {
                                websocket.close();
                            };
                        }
                    }, [username]);

                    const sendMessage = () => {
                        if (ws && input && recipient) {
                            ws.send(JSON.stringify({
                                type: 'message',
                                to: recipient,
                                content: input
                            }));
                            setInput('');
                        }
                    };

                    if (!username) {
                        return (
                            <div className="container">
                                <h1>Введите ваш никнейм</h1>
                                <div className="input">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        placeholder="Никнейм"
                                    />
                                    <button onClick={() => setUsername(input)}>Войти</button>
                                </div>
                            </div>
                        );
                    }

                    return (
                        <div className="container">
                            <h1>Messenger</h1>
                            <div style={{ marginBottom: '10px', color: '#666' }}>
                                Вы вошли как: <strong>{username}</strong>
                            </div>
                            <div className="chat">
                                {messages.map((msg, i) => (
                                    <div
                                        key={i}
                                        className={`message ${msg.sender === username ? 'sent' : 'received'}`}
                                    >
                                        <div><strong>{msg.sender}</strong></div>
                                        <div>{msg.content}</div>
                                        <div><small>{msg.timestamp.toLocaleString()}</small></div>
                                    </div>
                                ))}
                            </div>
                            <div className="input">
                                <input
                                    type="text"
                                    value={recipient}
                                    onChange={(e) => setRecipient(e.target.value)}
                                    placeholder="Получатель"
                                />
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Сообщение"
                                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                />
                                <button onClick={sendMessage}>Отправить</button>
                            </div>
                        </div>
                    );
                }

                ReactDOM.render(<App />, document.getElementById('root'));
            </script>
        </body>
    </html>
    """ 