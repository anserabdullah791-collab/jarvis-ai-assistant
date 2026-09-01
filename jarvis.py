#!/usr/bin/env python3
"""
JARVIS - Complete AI Assistant
Inspired by Iron Man's JARVIS
Built for macOS | Web-based | Voice + Text commands
No complex dependencies - works with macOS built-in features
"""

from flask import Flask, jsonify, request
import subprocess
import platform
import os
import json
import time
import datetime
import webbrowser
import requests

app = Flask(__name__)

# ===== JARVIS CAPABILITIES =====

def get_time():
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"

def get_date():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}"

def get_weather(city="Lahore"):
    try:
        # Open-Meteo free API (no key needed)
        geocode = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1", timeout=10).json()
        if geocode.get("results"):
            lat = geocode["results"][0]["latitude"]
            lon = geocode["results"][0]["longitude"]
            weather = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                timeout=10
            ).json()
            current = weather.get("current", {})
            temp = current.get("temperature_2m", 0)
            humidity = current.get("relative_humidity_2m", 0)
            wind = current.get("wind_speed_10m", 0)
            code = current.get("weather_code", 0)
            
            conditions = {
                0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
                45: "foggy", 48: "freezing fog", 51: "light drizzle", 53: "drizzle",
                55: "heavy drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
                71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
                80: "rain showers", 81: "heavy showers", 82: "violent showers",
                95: "thunderstorm", 96: "thunderstorm with hail", 99: "severe thunderstorm"
            }
            condition = conditions.get(code, "unknown")
            
            return f"Weather in {city}: {temp}°C, {condition}, humidity {humidity}%, wind {wind} km/h"
        return f"Could not find city: {city}"
    except Exception as e:
        return f"Weather service unavailable: {str(e)}"

def get_news():
    try:
        # Use Hacker News API (free, no key)
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:5]
        news = []
        for sid in story_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if story:
                news.append(f"- {story.get('title', 'Unknown')} ({story.get('score', 0)} upvotes)")
        return "Top tech news:\\n" + "\\n".join(news)
    except:
        return "News service temporarily unavailable"

def open_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}"

def open_app(app_name):
    try:
        subprocess.Popen(["open", "-a", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {app_name}"
    except:
        return f"Could not open {app_name}"

def system_info():
    info = {
        "OS": platform.system() + " " + platform.release(),
        "Machine": platform.machine(),
        "Processor": platform.processor() or "Unknown",
        "Python": platform.python_version(),
        "Hostname": platform.node()
    }
    # macOS specific
    if platform.system() == "Darwin":
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            info["CPU"] = cpu
            mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            info["RAM"] = f"{int(mem) // (1024**3)} GB"
        except:
            pass
    return json.dumps(info, indent=2)

def get_joke():
    try:
        resp = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        data = resp.json()
        return f"{data['setup']} ... {data['punchline']}"
    except:
        return "Why don't programmers like nature? It has too many bugs."

def search_wikipedia(query):
    try:
        resp = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_"),
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "No information found.")
        return f"No Wikipedia article found for {query}."
    except:
        return "Wikipedia search unavailable."

def get_ip_info():
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=10)
        data = resp.json()
        return f"Your IP: {data.get('ip')} | Location: {data.get('city')}, {data.get('country_name')} | ISP: {data.get('org')}"
    except:
        return "Could not fetch IP information."

def take_screenshot():
    if platform.system() == "Darwin":
        subprocess.Popen(["screencapture", "-x", os.path.expanduser("~/Desktop/jarvis_screenshot.png")])
        return "Screenshot saved to Desktop"
    return "Screenshots only available on macOS"

def set_volume(level):
    if platform.system() == "Darwin":
        try:
            vol = int(level) / 100
            subprocess.run(["osascript", "-e", f"set volume output volume {int(level)}"])
            return f"Volume set to {level}%"
        except:
            return "Could not set volume"
    return "Volume control only available on macOS"

def tell_time_with_voice():
    return get_time()

def process_command(command):
    """Main command processor - the brain of JARVIS"""
    cmd = command.lower().strip()
    response = {"action": "speak", "text": "", "data": None}
    
    # Greetings
    if any(w in cmd for w in ["hello", "hi", "hey jarvis", "jarvis"]):
        if "hello" in cmd or "hi " in cmd or cmd == "hi":
            response["text"] = "Hello sir. JARVIS is online and ready to assist you."
        elif "how are you" in cmd:
            response["text"] = "All systems operational, sir. How may I assist you?"
    
    # Time
    elif "time" in cmd and "what" in cmd:
        response["text"] = get_time()
        response["data"] = {"type": "time", "value": datetime.datetime.now().strftime("%H:%M")}
    
    # Date
    elif "date" in cmd or "today" in cmd and "what" in cmd:
        response["text"] = get_date()
    
    # Weather
    elif "weather" in cmd:
        city = "Lahore"
        words = cmd.split()
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = " ".join(words[idx+1:])
        response["text"] = get_weather(city)
        response["data"] = {"type": "weather", "city": city}
    
    # News
    elif "news" in cmd:
        response["text"] = get_news()
        response["data"] = {"type": "news"}
    
    # Open website
    elif cmd.startswith("open ") or cmd.startswith("go to "):
        site = cmd.replace("open ", "").replace("go to ", "")
        if "." not in site and site not in ["youtube", "google", "facebook", "twitter", "github", "gmail", "whatsapp"]:
            site_map = {
                "youtube": "youtube.com",
                "google": "google.com",
                "facebook": "facebook.com",
                "twitter": "twitter.com",
                "github": "github.com",
                "gmail": "gmail.com",
                "whatsapp": "web.whatsapp.com",
                "instagram": "instagram.com",
                "linkedin": "linkedin.com",
                "maps": "maps.apple.com",
                "app store": "apps.apple.com",
                "spotify": "open.spotify.com",
                "netflix": "netflix.com"
            }
            site = site_map.get(site, site + ".com")
        response["text"] = open_website(site)
        response["data"] = {"type": "open", "url": site if site.startswith("http") else "https://" + site}
    
    # Open app
    elif cmd.startswith("launch ") or cmd.startswith("start app "):
        app_name = cmd.replace("launch ", "").replace("start app ", "")
        response["text"] = open_app(app_name)
    
    # System info
    elif "system" in cmd and ("info" in cmd or "status" in cmd):
        response["text"] = "Retrieving system information, sir."
        response["data"] = {"type": "system", "info": system_info()}
    
    # Joke
    elif "joke" in cmd:
        response["text"] = get_joke()
    
    # Wikipedia
    elif "what is" in cmd or "who is" in cmd or "tell me about" in cmd or "search for" in cmd:
        query = cmd.replace("what is ", "").replace("who is ", "").replace("tell me about ", "").replace("search for ", "")
        if "wikipedia" in query:
            query = query.replace("wikipedia ", "").replace(" on wikipedia", "")
        response["text"] = search_wikipedia(query)
        response["data"] = {"type": "wiki", "query": query}
    
    # Screenshot
    elif "screenshot" in cmd:
        response["text"] = take_screenshot()
    
    # Volume
    elif "volume" in cmd:
        for word in cmd.split():
            if word.isdigit():
                response["text"] = set_volume(word)
                break
        else:
            if "up" in cmd:
                response["text"] = "Increasing volume, sir."
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings)) + 10"], capture_output=True)
            elif "down" in cmd:
                response["text"] = "Decreasing volume, sir."
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings)) - 10"], capture_output=True)
            else:
                response["text"] = "Say volume up, volume down, or volume followed by a number."
    
    # IP info
    elif "ip address" in cmd or "my ip" in cmd:
        response["text"] = get_ip_info()
    
    # Calculate
    elif "calculate" in cmd or cmd.startswith("what is") and any(c in cmd for c in "+-*/x"):
        expr = cmd.replace("calculate ", "").replace("what is ", "").replace("what's ", "")
        # Sanitize
        expr = expr.replace("x", "*").replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        try:
            # Only allow safe math
            allowed = set("0123456789+-*/.() ")
            if all(c in allowed for c in expr):
                result = eval(expr)
                response["text"] = f"The answer is {result}"
                response["data"] = {"type": "calc", "expression": expr, "result": result}
            else:
                response["text"] = "I can only perform basic math operations, sir."
        except:
            response["text"] = "I couldn't calculate that, sir."
    
    # Mac controls
    elif "brightness" in cmd:
        response["text"] = "Brightness control requires manual adjustment, sir. Use your keyboard brightness keys."
    
    # Sleep / Lock
    elif "sleep" in cmd:
        if platform.system() == "Darwin":
            subprocess.run(["pmset", "sleepnow"], capture_output=True)
            response["text"] = "Putting the system to sleep, sir."
        else:
            response["text"] = "Sleep command only available on macOS."
    
    elif "lock" in cmd:
        if platform.system() == "Darwin":
            subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
            response["text"] = "Locking the screen, sir."
        else:
            response["text"] = "Lock command only available on macOS."
    
    # Shutdown / Restart (with confirmation)
    elif "shutdown" in cmd:
        response["text"] = "Are you sure you want to shut down? Please confirm."
        response["data"] = {"type": "confirm", "action": "shutdown"}
    
    elif "restart" in cmd:
        response["text"] = "Are you sure you want to restart? Please confirm."
        response["data"] = {"type": "confirm", "action": "restart"}
    
    # Play music
    elif "play" in cmd and ("music" in cmd or "song" in cmd):
        song = cmd.replace("play ", "").replace("music", "").replace("song", "").strip()
        if song:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            response["text"] = f"Searching for {song} on YouTube, sir."
        else:
            webbrowser.open("https://www.youtube.com/results?search_query=music")
            response["text"] = "Opening YouTube music, sir."
    
    # Clear / Reset
    elif "clear" in cmd or "reset" in cmd:
        response["text"] = "Interface cleared, sir."
        response["data"] = {"type": "clear"}
    
    # Help
    elif "help" in cmd or "what can you do" in cmd:
        response["text"] = "I can help you with: time and date, weather, news, web search, opening apps and websites, system information, Wikipedia, jokes, calculations, screenshots, volume control, playing music, and system controls. Just ask, sir."
        response["data"] = {"type": "help"}
    
    # Thank you
    elif "thank" in cmd:
        response["text"] = "Always a pleasure, sir."
    
    # Goodbye
    elif "goodbye" in cmd or "bye" in cmd or "shut down jarvis" in cmd:
        response["text"] = "Goodbye, sir. JARVIS signing off."
        response["data"] = {"type": "shutdown_jarvis"}
    
    # Default - try to search
    else:
        response["text"] = f"I'm not sure how to help with that yet, sir. Would you like me to search the web for '{command}'?"
        response["data"] = {"type": "search_suggest", "query": command}
    
    return response

# ===== WEB UI =====

HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>J.A.R.V.I.S</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #000;
    color: #00aaff;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    overflow: hidden;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.header {
    position: fixed; top: 0; width: 100%; padding: 15px;
    display: flex; justify-content: space-between; align-items: center;
    z-index: 100;
}
.header .logo { font-size: 14px; letter-spacing: 4px; color: #00aaff; opacity: 0.6; }
.header .status { font-size: 11px; color: #00ff88; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00ff88; margin-right: 5px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

.reactor {
    position: relative; width: 350px; height: 350px; margin-top: 60px;
    display: flex; align-items: center; justify-content: center;
}
.reactor-ring {
    position: absolute; border-radius: 50%; border: 2px solid rgba(0, 170, 255, 0.3);
    animation: spin 10s linear infinite;
}
.r1 { width: 350px; height: 350px; border: 1px solid rgba(0, 170, 255, 0.2); }
.r2 { width: 280px; height: 280px; border: 2px solid rgba(0, 170, 255, 0.3); animation: spin 7s linear infinite reverse; }
.r3 { width: 210px; height: 210px; border: 1px solid rgba(0, 170, 255, 0.4); animation: spin 5s linear infinite; }
.r4 { width: 140px; height: 140px; border: 2px solid rgba(0, 170, 255, 0.5); animation: spin 3s linear infinite reverse; }
.r-core {
    width: 80px; height: 80px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 170, 255, 0.8), rgba(0, 100, 200, 0.3), transparent);
    box-shadow: 0 0 60px rgba(0, 170, 255, 0.6), inset 0 0 20px rgba(0, 170, 255, 0.3);
    animation: corepulse 2s ease-in-out infinite;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; color: #fff; letter-spacing: 2px;
}
@keyframes corepulse { 0%,100% { transform: scale(1); box-shadow: 0 0 60px rgba(0,170,255,0.6); } 50% { transform: scale(1.1); box-shadow: 0 0 80px rgba(0,170,255,0.8); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.reactor-listening .r-core { background: radial-gradient(circle, rgba(255, 200, 0, 0.8), rgba(255, 100, 0, 0.3), transparent); box-shadow: 0 0 80px rgba(255, 200, 0, 0.6); }
.reactor-thinking .r-core { background: radial-gradient(circle, rgba(150, 150, 255, 0.8), rgba(100, 100, 200, 0.3), transparent); }

.reactor-segments { position: absolute; width: 350px; height: 350px; }
.segment {
    position: absolute; width: 4px; height: 20px; background: rgba(0, 170, 255, 0.6);
    top: 50%; left: 50%; transform-origin: 0 175px;
}

.controls {
    position: fixed; bottom: 0; width: 100%; padding: 20px;
    display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.mic-btn {
    width: 60px; height: 60px; border-radius: 50%; border: 2px solid #00aaff;
    background: rgba(0, 170, 255, 0.1); color: #00aaff; cursor: pointer;
    font-size: 24px; display: flex; align-items: center; justify-content: center;
    transition: all 0.3s;
}
.mic-btn:hover { background: rgba(0, 170, 255, 0.3); box-shadow: 0 0 20px rgba(0, 170, 255, 0.5); }
.mic-btn.listening { background: rgba(255, 200, 0, 0.3); border-color: #ffc800; box-shadow: 0 0 30px rgba(255, 200, 0, 0.6); animation: pulse 1s infinite; }
.command-input {
    width: 80%; max-width: 600px; padding: 12px 20px; border-radius: 25px;
    background: rgba(0, 170, 255, 0.05); border: 1px solid rgba(0, 170, 255, 0.3);
    color: #00aaff; font-size: 14px; outline: none; font-family: 'Helvetica Neue', Arial;
}
.command-input:focus { border-color: rgba(0, 170, 255, 0.6); box-shadow: 0 0 15px rgba(0, 170, 255, 0.2); }
.command-input::placeholder { color: rgba(0, 170, 255, 0.3); }
.send-btn {
    position: absolute; right: 10%; top: 50%; transform: translateY(-50%);
    background: none; border: none; color: #00aaff; cursor: pointer; font-size: 18px;
}

.conversation {
    position: fixed; top: 80px; right: 20px; width: 350px; max-height: 60vh;
    overflow-y: auto; padding: 10px;
}
.msg {
    margin-bottom: 10px; padding: 10px 15px; border-radius: 15px; font-size: 13px;
    line-height: 1.5; opacity: 0; animation: fadeIn 0.3s forwards;
}
@keyframes fadeIn { to { opacity: 1; } }
.msg.user { background: rgba(0, 170, 255, 0.1); border: 1px solid rgba(0, 170, 255, 0.2); text-align: right; margin-left: 40px; }
.msg.jarvis { background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.2); text-align: left; margin-right: 40px; }
.msg .label { font-size: 10px; color: rgba(255,255,255,0.3); margin-bottom: 3px; }

.status-text {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, 100px);
    font-size: 13px; color: rgba(0, 170, 255, 0.6); letter-spacing: 2px;
    text-align: center; width: 300px;
}

.quick-commands {
    position: fixed; top: 80px; left: 20px; display: flex; flex-direction: column; gap: 8px;
}
.quick-cmd {
    padding: 8px 15px; border-radius: 20px; background: rgba(0, 170, 255, 0.05);
    border: 1px solid rgba(0, 170, 255, 0.2); color: rgba(0, 170, 255, 0.6);
    font-size: 11px; cursor: pointer; transition: all 0.2s;
}
.quick-cmd:hover { background: rgba(0, 170, 255, 0.15); border-color: rgba(0, 170, 255, 0.5); color: #00aaff; }

.data-display {
    position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%);
    width: 90%; max-width: 600px; max-height: 200px; overflow-y: auto;
    display: none;
}
.data-display.active { display: block; }
.data-card {
    background: rgba(0, 170, 255, 0.05); border: 1px solid rgba(0, 170, 255, 0.2);
    border-radius: 10px; padding: 15px; margin-top: 5px; font-size: 12px;
}
.data-card h4 { color: #00aaff; margin-bottom: 8px; font-size: 13px; }
.data-card pre { color: rgba(0, 255, 136, 0.7); white-space: pre-wrap; font-size: 11px; }
</style>
</head>
<body>

<div class="header">
    <div class="logo">J.A.R.V.I.S</div>
    <div class="status"><span class="status-dot"></span>ONLINE</div>
</div>

<div class="quick-commands">
    <div class="quick-cmd" onclick="sendCommand('what time is it')">Time</div>
    <div class="quick-cmd" onclick="sendCommand('what is the date')">Date</div>
    <div class="quick-cmd" onclick="sendCommand('weather in Lahore')">Weather</div>
    <div class="quick-cmd" onclick="sendCommand('news')">News</div>
    <div class="quick-cmd" onclick="sendCommand('tell me a joke')">Joke</div>
    <div class="quick-cmd" onclick="sendCommand('system info')">System</div>
    <div class="quick-cmd" onclick="sendCommand('my ip address')">IP</div>
    <div class="quick-cmd" onclick="sendCommand('help')">Help</div>
</div>

<div class="reactor" id="reactor">
    <div class="reactor-ring r1"></div>
    <div class="reactor-segments" id="segments"></div>
    <div class="reactor-ring r2"></div>
    <div class="reactor-ring r3"></div>
    <div class="reactor-ring r4"></div>
    <div class="r-core" id="core">JARVIS</div>
</div>

<div class="status-text" id="statusText">Click the mic or type a command, sir</div>

<div class="conversation" id="conversation"></div>

<div class="data-display" id="dataDisplay"></div>

<div class="controls">
    <button class="mic-btn" id="micBtn" onclick="toggleVoice()">&#127908;</button>
    <div style="position:relative;width:80%;max-width:600px;">
        <input type="text" class="command-input" id="commandInput" placeholder="Type a command or ask a question..." onkeypress="if(event.key==='Enter') sendInput()">
        <button class="send-btn" onclick="sendInput()">&#9654;</button>
    </div>
</div>

<script>
// Create reactor segments
const segContainer = document.getElementById('segments');
for (let i = 0; i < 24; i++) {
    const seg = document.createElement('div');
    seg.className = 'segment';
    seg.style.transform = `rotate(${i * 15}deg) translateX(0)`;
    segContainer.appendChild(seg);
}

let recognition = null;
let isListening = false;

// Web Speech API
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        document.getElementById('commandInput').value = transcript;
        if (e.results[0].isFinal) {
            sendInput();
        }
    };
    
    recognition.onerror = (e) => {
        setReactorState('idle');
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        addMessage('jarvis', 'Voice recognition error: ' + e.error + '. You can still type commands, sir.');
    };
    
    recognition.onend = () => {
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        if (document.getElementById('commandInput').value.trim()) {
            sendInput();
        } else {
            setReactorState('idle');
        }
    };
}

function toggleVoice() {
    if (!recognition) {
        addMessage('jarvis', 'Voice recognition not available in this browser. Please use Safari or Chrome, or type your command.');
        return;
    }
    if (isListening) {
        recognition.stop();
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        setReactorState('idle');
    } else {
        recognition.start();
        isListening = true;
        document.getElementById('micBtn').classList.add('listening');
        setReactorState('listening');
        document.getElementById('statusText').textContent = 'Listening, sir...';
    }
}

function setReactorState(state) {
    const reactor = document.getElementById('reactor');
    reactor.classList.remove('reactor-listening', 'reactor-thinking');
    const core = document.getElementById('core');
    const status = document.getElementById('statusText');
    
    if (state === 'listening') {
        reactor.classList.add('reactor-listening');
        core.textContent = 'LISTEN';
        status.textContent = 'Listening, sir...';
    } else if (state === 'thinking') {
        reactor.classList.add('reactor-thinking');
        core.textContent = 'PROC';
        status.textContent = 'Processing, sir...';
    } else {
        core.textContent = 'JARVIS';
        status.textContent = 'Awaiting your command, sir';
    }
}

function sendCommand(cmd) {
    document.getElementById('commandInput').value = cmd;
    sendInput();
}

function sendInput() {
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    
    input.value = '';
    addMessage('user', cmd);
    setReactorState('thinking');
    
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
    })
    .then(r => r.json())
    .then(data => {
        setReactorState('idle');
        addMessage('jarvis', data.text);
        speak(data.text);
        
        if (data.data) {
            displayData(data.data);
        }
    })
    .catch(e => {
        setReactorState('idle');
        addMessage('jarvis', 'Connection error, sir. Please try again.');
    });
}

function addMessage(sender, text) {
    const conv = document.getElementById('conversation');
    const msg = document.createElement('div');
    msg.className = 'msg ' + sender;
    msg.innerHTML = `<div class="label">${sender === 'user' ? 'YOU' : 'JARVIS'}</div>${text}`;
    conv.appendChild(msg);
    conv.scrollTop = conv.scrollHeight;
}

function speak(text) {
    if ('speechSynthesis' in window) {
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 0.95;
        utter.pitch = 0.9;
        utter.volume = 0.8;
        
        // Try to find a male British voice
        const voices = speechSynthesis.getVoices();
        const preferred = voices.find(v => v.name.includes('Daniel') || v.name.includes('Arthur') || v.name.includes('Oliver'));
        if (preferred) utter.voice = preferred;
        
        speechSynthesis.speak(utter);
    }
}

function displayData(data) {
    const display = document.getElementById('dataDisplay');
    
    if (data.type === 'time') {
        display.innerHTML = `<div class="data-card"><h4>CURRENT TIME</h4><pre>${data.value}</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'weather') {
        display.innerHTML = `<div class="data-card"><h4>WEATHER - ${data.city}</h4><pre>Loading...</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'system') {
        display.innerHTML = `<div class="data-card"><h4>SYSTEM INFO</h4><pre>${data.info}</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'help') {
        display.innerHTML = `<div class="data-card"><h4>JARVIS CAPABILITIES</h4>
        <pre>Time and Date
Weather (any city)
Tech News
Open websites and apps
Wikipedia search
Jokes
Math calculations
System information
IP address
Screenshots (macOS)
Volume control (macOS)
Play music (YouTube)
System sleep/lock (macOS)
Voice commands</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'news') {
        display.innerHTML = `<div class="data-card"><h4>TECH NEWS</h4><pre>Check conversation panel for details</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'wiki') {
        display.innerHTML = `<div class="data-card"><h4>WIKIPEDIA - ${data.query}</h4><pre>See conversation panel</pre></div>`;
        display.classList.add('active');
    } else if (data.type === 'clear') {
        document.getElementById('conversation').innerHTML = '';
        display.classList.remove('active');
    } else if (data.type === 'shutdown_jarvis') {
        setTimeout(() => { window.close(); }, 2000);
    }
}

// Load voices
if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = () => {};
}

// Boot sequence
setTimeout(() => {
    addMessage('jarvis', 'JARVIS online. All systems operational. How may I assist you, sir?');
    speak('JARVIS online. All systems operational. How may I assist you, sir?');
}, 1000);
</script>

</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/api/command', methods=['POST'])
def api_command():
    data = request.json
    command = data.get('command', '')
    result = process_command(command)
    return jsonify(result)

if __name__ == '__main__':
    print("=" * 50)
    print("  J.A.R.V.I.S - AI Assistant Starting...")
    print("  Open your browser to: http://localhost:7654")
    print("  Click the mic icon to speak")
    print("  Or type your commands")
    print("  Press Ctrl+C to shut down JARVIS")
    print("=" * 50)
    webbrowser.open("http://localhost:7654")
    app.run(host='0.0.0.0', port=7654, debug=False)
