import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openjarvis.tools.calculator import CalculatorTool

app = FastAPI(title="Jarvis Calculator App")
calc_tool = CalculatorTool()

class CalcRequest(BaseModel):
    expression: str

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jarvis Smart Calculator</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-color: #0f172a;
                --calc-bg: rgba(30, 41, 59, 0.7);
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent: #3b82f6;
                --accent-hover: #60a5fa;
                --border: rgba(255,255,255,0.1);
            }
            body {
                font-family: 'Outfit', sans-serif;
                background: linear-gradient(135deg, var(--bg-color), #000000);
                color: var(--text-main);
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: var(--calc-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--border);
                padding: 2.5rem;
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            h1 {
                margin-top: 0;
                font-weight: 600;
                font-size: 1.8rem;
                background: -webkit-linear-gradient(45deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p.subtitle {
                color: var(--text-muted);
                font-size: 0.9rem;
                margin-bottom: 2rem;
            }
            input[type="text"] {
                width: 100%;
                box-sizing: border-box;
                background: rgba(0,0,0,0.2);
                border: 1px solid var(--border);
                color: white;
                font-family: 'Outfit', monospace;
                font-size: 1.2rem;
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                outline: none;
                transition: border-color 0.3s ease;
            }
            input[type="text"]:focus {
                border-color: var(--accent);
            }
            button {
                width: 100%;
                background: var(--accent);
                color: white;
                border: none;
                padding: 1rem;
                font-size: 1.1rem;
                font-weight: 600;
                border-radius: 12px;
                cursor: pointer;
                transition: background 0.3s ease, transform 0.1s ease;
            }
            button:hover {
                background: var(--accent-hover);
            }
            button:active {
                transform: scale(0.98);
            }
            .result-box {
                margin-top: 1.5rem;
                padding: 1rem;
                background: rgba(0,0,0,0.3);
                border-radius: 12px;
                min-height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
                font-weight: 400;
                word-break: break-all;
                border: 1px solid transparent;
                transition: all 0.3s ease;
            }
            .result-box.success {
                border-color: #4ade80;
                color: #4ade80;
            }
            .result-box.error {
                border-color: #f87171;
                color: #f87171;
            }
            .loader {
                display: none;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Jarvis Calculator</h1>
            <p class="subtitle">Powered by OpenJarvis Rust Backend</p>
            
            <input type="text" id="expr" placeholder="e.g. 2^10 or sin(pi/4)" onkeypress="handleEnter(event)" autocomplete="off">
            <button onclick="calculate()">Evaluate</button>
            
            <div id="result" class="result-box">
                <span id="result-text">Waiting for input...</span>
                <div id="loader" class="loader"></div>
            </div>
        </div>

        <script>
            function handleEnter(e) {
                if (e.key === 'Enter') calculate();
            }

            async function calculate() {
                const expr = document.getElementById('expr').value;
                if (!expr) return;

                const resultBox = document.getElementById('result');
                const resultText = document.getElementById('result-text');
                const loader = document.getElementById('loader');

                resultBox.className = 'result-box';
                resultText.style.display = 'none';
                loader.style.display = 'block';

                try {
                    const response = await fetch('/calculate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ expression: expr })
                    });
                    
                    const data = await response.json();
                    
                    loader.style.display = 'none';
                    resultText.style.display = 'block';
                    
                    if (data.success) {
                        resultBox.classList.add('success');
                        resultText.textContent = '= ' + data.result;
                    } else {
                        resultBox.classList.add('error');
                        resultText.textContent = data.error;
                    }
                } catch (err) {
                    loader.style.display = 'none';
                    resultText.style.display = 'block';
                    resultBox.classList.add('error');
                    resultText.textContent = "Network Error";
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/calculate")
def calculate_api(req: CalcRequest):
    res = calc_tool.execute(expression=req.expression)
    if res.success:
        return {"success": True, "result": res.content}
    return {"success": False, "error": res.content}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
