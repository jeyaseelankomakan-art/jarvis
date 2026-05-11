import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Jarvis Voice App")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JARVIS_API_URL = "http://127.0.0.1:8000/v1/chat/completions"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis Voice Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0f172a;
            --surface: rgba(30, 41, 59, 0.7);
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.5);
            --text: #f8fafc;
            --muted: #94a3b8;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            background: radial-gradient(circle at center, #1e293b 0%, #020617 100%);
        }

        .container {
            width: 90%;
            max-width: 600px;
            height: 80vh;
            background: var(--surface);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 32px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            padding: 30px;
            position: relative;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
        }

        .header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }

        .header p {
            margin: 5px 0 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        .chat-log {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        .chat-log::-webkit-scrollbar {
            width: 6px;
        }
        .chat-log::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }

        .message {
            max-width: 80%;
            padding: 14px 18px;
            border-radius: 20px;
            font-size: 1rem;
            line-height: 1.5;
            animation: fadeIn 0.3s ease-out;
        }

        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #38bdf8, #2563eb);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text);
            border-bottom-left-radius: 4px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .controls {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 20px;
            margin-top: auto;
            position: relative;
        }

        .text-controls {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }

        .text-input {
            flex: 1;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.06);
            color: var(--text);
            padding: 10px 12px;
            font-size: 0.95rem;
            outline: none;
        }

        .text-input::placeholder {
            color: var(--muted);
        }

        .send-button {
            border: none;
            border-radius: 12px;
            padding: 10px 14px;
            background: linear-gradient(135deg, #0ea5e9, #2563eb);
            color: white;
            font-weight: 600;
            cursor: pointer;
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .mic-button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            font-size: 32px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 0 20px var(--primary-glow);
            position: relative;
            z-index: 10;
        }

        .mic-button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px var(--primary-glow);
        }

        .mic-button.listening {
            animation: pulse 1.5s infinite;
            background: linear-gradient(135deg, #ef4444, #b91c1c);
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);
        }

        .mic-button.thinking {
            animation: spinPulse 2s infinite;
            background: linear-gradient(135deg, #10b981, #047857);
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.6);
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        @keyframes spinPulse {
            0% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(180deg); }
            100% { transform: scale(1) rotate(360deg); }
        }

        .status {
            position: absolute;
            bottom: -25px;
            font-size: 0.85rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <h1>Jarvis UI</h1>
            <p>Advanced Agentic Voice Interface</p>
        </div>

        <div class="chat-log" id="chatLog">
            <div class="message assistant">Hello sir. I am online and ready. Tap the microphone to speak.</div>
        </div>

        <div class="controls">
            <button class="mic-button" id="micBtn">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="22"></line>
                </svg>
            </button>
            <div class="status" id="statusText">Ready</div>
        </div>

        <div class="text-controls">
            <input id="textInput" class="text-input" type="text" placeholder="Type a message if mic fails..." />
            <button id="sendBtn" class="send-button">Send</button>
        </div>
    </div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const chatLog = document.getElementById('chatLog');
        const statusText = document.getElementById('statusText');
        const textInput = document.getElementById('textInput');
        const sendBtn = document.getElementById('sendBtn');
        
        let isListening = false;
        let isThinking = false;
        
        // Setup Web Speech API for recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        
        // Setup Speech Synthesis for voice output
        const synth = window.speechSynthesis;
        let voices = [];

        function loadVoices() {
            voices = synth.getVoices();
        }
        loadVoices();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoices;
        }

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add('listening');
                statusText.innerText = "Listening...";
                synth.cancel(); // stop current speech if user interrupts
            };

            recognition.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                appendMessage(transcript, 'user');
                
                isListening = false;
                micBtn.classList.remove('listening');
                
                await sendToJarvis(transcript);
            };

            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                isListening = false;
                micBtn.classList.remove('listening');
                const msg = speechErrorMessage(event.error);
                statusText.innerText = msg;
                appendMessage(msg, 'assistant');
            };

            recognition.onend = () => {
                if(isListening) {
                    isListening = false;
                    micBtn.classList.remove('listening');
                    statusText.innerText = "Ready";
                }
            };
        } else {
            statusText.innerText = "Speech API not supported in this browser.";
            micBtn.disabled = true;
        }

        micBtn.addEventListener('click', () => {
            if (isThinking) return;
            if (isListening) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (err) {
                    const msg = "Microphone could not start. Check browser permission and try again.";
                    console.error(err);
                    statusText.innerText = msg;
                    appendMessage(msg, 'assistant');
                }
            }
        });

        sendBtn.addEventListener('click', async () => {
            if (isThinking) return;
            const text = textInput.value.trim();
            if (!text) return;
            appendMessage(text, 'user');
            textInput.value = '';
            await sendToJarvis(text);
        });

        textInput.addEventListener('keydown', async (event) => {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            sendBtn.click();
        });

        function speechErrorMessage(error) {
            if (error === 'not-allowed' || error === 'service-not-allowed') {
                return 'Microphone permission denied. Allow mic access in browser site settings and reload.';
            }
            if (error === 'audio-capture') {
                return 'No microphone detected. Check your input device settings.';
            }
            if (error === 'no-speech') {
                return 'No speech detected. Please speak clearly and try again.';
            }
            if (error === 'network') {
                return 'Speech recognition network error. Check internet and try Chrome/Edge.';
            }
            if (error === 'aborted') {
                return 'Listening stopped.';
            }
            return `Speech recognition error: ${error}`;
        }

        function appendMessage(text, sender) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            msgDiv.innerText = text;
            chatLog.appendChild(msgDiv);
            chatLog.scrollTop = chatLog.scrollHeight;
        }

        // Conversation history array
        let conversationHistory = [
            { role: "system", content: "You are Jarvis, an AI assistant. Give very concise, short conversational answers without formatting." }
        ];

        async function sendToJarvis(prompt) {
            isThinking = true;
            micBtn.classList.add('thinking');
            sendBtn.disabled = true;
            statusText.innerText = "Jarvis is thinking...";

            conversationHistory.push({ role: "user", content: prompt });

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: conversationHistory })
                });

                const data = await response.json();
                
                if (data.reply) {
                    appendMessage(data.reply, 'assistant');
                    conversationHistory.push({ role: "assistant", content: data.reply });
                    speak(data.reply);
                } else {
                    appendMessage("Error processing request.", 'assistant');
                    statusText.innerText = "Ready";
                }
            } catch (err) {
                console.error(err);
                appendMessage("Failed to connect to backend.", 'assistant');
                statusText.innerText = "Ready";
            } finally {
                isThinking = false;
                micBtn.classList.remove('thinking');
                sendBtn.disabled = false;
            }
        }

        function speak(text) {
            statusText.innerText = "Speaking...";
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Try to find a good British male voice for Jarvis, fallback to any available
            let selectedVoice = voices.find(v => v.name.includes('Google UK English Male') || v.name.includes('Hazel') || v.name.includes('David'));
            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }
            
            utterance.rate = 1.0;
            utterance.pitch = 0.9;
            
            utterance.onend = () => {
                if(!isThinking && !isListening) {
                    statusText.innerText = "Ready";
                }
            };
            
            synth.speak(utterance);
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/api/chat")
async def chat_proxy(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    
    payload = {
        "model": "gemma4:latest",
        "messages": messages
    }
    
    try:
        response = requests.post(JARVIS_API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            return {"reply": reply}
        else:
            return {"reply": "Sorry sir, my core connection is currently failing."}
    except Exception as e:
        return {"reply": f"System error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
