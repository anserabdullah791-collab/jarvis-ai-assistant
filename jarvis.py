#!/usr/bin/env python3
"""
JARVIS v4.0 — Complete AI Assistant
- macOS native voice (say command)
- Auto-listening wake word ("Jarvis")
- GitHub clone/install/download
- Code execution (Python, JS, HTML)
- Claude AI integration
- Desktop control (AppleScript)
- VS Code + Terminal integration
- 60+ skills
- Autonomous task execution
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
import threading

app = Flask(__name__)
IS_MAC = platform.system() == "Darwin"

# ===== NATIVE VOICE =====
def jarvis_speak(text):
    if IS_MAC:
        clean = text.replace(" sir", "").replace("Sir, ", "").replace("\n", " ")
        try:
            subprocess.Popen(["say", "-v", "Daniel", "-r", "180", clean], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            subprocess.Popen(["say", "-r", "180", clean], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return text

# ===== APPLESCRIPT =====
def applescript(script):
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# ===== DESKTOP CONTROL =====
def open_app(app_name):
    if IS_MAC:
        r = applescript(f'tell application "{app_name}" to activate')
        if "Error" in r:
            subprocess.Popen(["open", "-a", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {app_name}, sir."
    return "Only available on macOS."

def close_app(app_name):
    if IS_MAC:
        applescript(f'tell application "{app_name}" to quit')
        return f"Closing {app_name}, sir."
    return "Only available on macOS."

def open_vscode(path=None):
    if IS_MAC:
        if path:
            subprocess.Popen(["code", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening VS Code with {path}, sir."
        open_app("Visual Studio Code")
        return "Opening VS Code, sir."
    return "Only available on macOS."

def open_github_desktop():
    if IS_MAC:
        open_app("GitHub Desktop")
        return "Opening GitHub Desktop, sir."
    return "Only available on macOS."

def open_terminal():
    if IS_MAC:
        applescript('tell application "Terminal" to activate')
        return "Opening Terminal, sir."
    return "Only available on macOS."

def run_terminal_command(cmd):
    if IS_MAC:
        script = f'tell application "Terminal"\nactivate\ndo script "{cmd}"\nend tell'
        applescript(script)
        return f"Running in Terminal: {cmd}"
    return "Only available on macOS."

def type_in_app(text):
    if IS_MAC:
        safe = text.replace('"', '\\"')
        applescript(f'tell application "System Events" to keystroke "{safe}"')
        return f"Typed: {text}"
    return "Only available on macOS."

def press_key(key):
    if IS_MAC:
        key_map = {"enter":"return","return":"return","tab":"tab","space":"space","escape":"escape","esc":"escape","delete":"delete","backspace":"delete","up":"arrow up","down":"arrow down","left":"arrow left","right":"arrow right"}
        applescript(f'tell application "System Events" to keystroke "{key_map.get(key.lower(), key.lower())}"')
        return f"Pressed {key}"
    return "Only available on macOS."

def copy_paste():
    if IS_MAC:
        applescript('tell application "System Events" to keystroke "c" using command down')
        time.sleep(0.2)
        applescript('tell application "System Events" to keystroke "v" using command down')
        return "Copy and paste done, sir."
    return "Only available on macOS."

def take_screenshot():
    if IS_MAC:
        subprocess.Popen(["screencapture", "-x", os.path.expanduser("~/Desktop/jarvis_screenshot.png")])
        return "Screenshot saved to Desktop, sir."
    return "Only available on macOS."

def set_volume(level):
    if IS_MAC:
        applescript(f"set volume output volume {int(level)}")
        return f"Volume set to {level}%, sir."
    return "Only available on macOS."

def get_volume():
    if IS_MAC:
        vol = applescript('output volume of (get volume settings)')
        return f"Volume is {vol}%, sir."
    return "Only available on macOS."

def open_folder(name):
    if IS_MAC:
        paths = {"desktop":"~/Desktop","documents":"~/Documents","downloads":"~/Downloads","pictures":"~/Pictures","music":"~/Music","movies":"~/Movies","applications":"/Applications","home":"~"}
        subprocess.Popen(["open", os.path.expanduser(paths.get(name.lower(), name))])
        return f"Opening {name}, sir."
    return "Only available on macOS."

def create_note(title, content):
    if IS_MAC:
        applescript(f'tell application "Notes"\ntell account "iCloud"\nmake new note with properties {{name:"{title}", body:"{content}"}}\nend tell\nend tell')
        return f"Note '{title}' created, sir."
    return "Only available on macOS."

def create_reminder(text):
    if IS_MAC:
        applescript(f'tell application "Reminders" to make new reminder with properties {{name:"{text}"}}')
        return f"Reminder: {text}"
    return "Only available on macOS."

def list_running_apps():
    if IS_MAC:
        result = applescript('tell application "System Events" to get name of every process whose background only is false')
        return f"Running: {result}"
    return "Only available on macOS."

def lock_screen():
    if IS_MAC:
        subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
        return "Locking screen, sir."
    return "Only available on macOS."

def sleep_mac():
    if IS_MAC:
        subprocess.run(["pmset", "sleepnow"], capture_output=True)
        return "Goodnight, sir."
    return "Only available on macOS."

def restart_mac():
    if IS_MAC:
        subprocess.Popen(["osascript", "-e", 'tell application "System Events" to restart'])
        return "Restarting, sir."
    return "Only available on macOS."

def shutdown_mac():
    if IS_MAC:
        subprocess.Popen(["osascript", "-e", 'tell application "System Events" to shut down'])
        return "Shutting down, sir."
    return "Only available on macOS."

def empty_trash():
    if IS_MAC:
        applescript('tell application "Finder" to empty trash')
        return "Emptying trash, sir."
    return "Only available on macOS."

def system_info():
    info = {"OS": platform.system()+" "+platform.release(), "Machine": platform.machine(), "Python": platform.python_version()}
    if IS_MAC:
        try:
            info["CPU"] = subprocess.check_output(["sysctl","-n","machdep.cpu.brand_string"], text=True).strip()
            mem = subprocess.check_output(["sysctl","-n","hw.memsize"], text=True).strip()
            info["RAM"] = f"{int(mem)//(1024**3)} GB"
        except: pass
    return json.dumps(info, indent=2)

# ===== GITHUB =====
def git_clone(url):
    if IS_MAC:
        name = url.split("/")[-1].replace(".git","")
        target = os.path.expanduser(f"~/Desktop/{name}")
        subprocess.run(["git","clone",url,target], capture_output=True)
        return f"Cloned {name} to Desktop, sir."
    return "Only available on macOS."

def git_push(message="Update"):
    if IS_MAC:
        run_terminal_command(f"git add . && git commit -m '{message}' && git push")
        return "Committing and pushing, sir."
    return "Only available on macOS."

def git_init_repo(name):
    if IS_MAC:
        path = os.path.expanduser(f"~/Desktop/{name}")
        os.makedirs(path, exist_ok=True)
        subprocess.run(["git","init"], cwd=path, capture_output=True)
        return f"Git repo '{name}' initialized on Desktop, sir."
    return "Only available on macOS."

def github_install(url):
    """Clone and run/install a GitHub project"""
    if IS_MAC:
        name = url.split("/")[-1].replace(".git","")
        target = os.path.expanduser(f"~/Desktop/{name}")
        subprocess.run(["git","clone",url,target], capture_output=True)
        # Check for install files
        if os.path.exists(os.path.join(target, "requirements.txt")):
            subprocess.run(["pip3","install","-r",os.path.join(target,"requirements.txt")], capture_output=True)
        if os.path.exists(os.path.join(target, "package.json")):
            subprocess.run(["npm","install"], cwd=target, capture_output=True)
        return f"Installed {name} from GitHub to your Desktop, sir. Dependencies installed."
    return "Only available on macOS."

def github_search(query):
    """Search GitHub for repos"""
    try:
        resp = requests.get(f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page=5", timeout=10)
        data = resp.json()
        results = []
        for r in data.get("items", []):
            results.append(f"{r['full_name']} - {r['description'][:60] if r['description'] else 'No description'} ({r['stargazers_count']} stars)")
        return "GitHub search results: " + " | ".join(results)
    except:
        return "GitHub search unavailable, sir."

def download_github_file(url, filename):
    """Download a single file from GitHub raw URL"""
    if IS_MAC:
        try:
            resp = requests.get(url, timeout=10)
            path = os.path.expanduser(f"~/Desktop/{filename}")
            with open(path, 'w') as f:
                f.write(resp.text)
            return f"Downloaded {filename} to Desktop, sir."
        except:
            return "Download failed, sir."
    return "Only available on macOS."

# ===== CODE EXECUTION =====
def run_python(code):
    """Execute Python code and return output"""
    try:
        result = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=10)
        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        return f"Output: {output}" if output else "Code executed, no output."
    except Exception as e:
        return f"Error: {str(e)}"

def create_python_file(filename, code):
    """Create a Python file on Desktop"""
    path = os.path.expanduser(f"~/Desktop/{filename}")
    with open(path, 'w') as f:
        f.write(code)
    return f"Created {filename} on Desktop, sir."

def run_python_file(filename):
    """Run a Python file"""
    path = os.path.expanduser(f"~/Desktop/{filename}")
    if os.path.exists(path):
        result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=15)
        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        return f"Output: {output}" if output else "Ran successfully."
    return f"File {filename} not found on Desktop, sir."

def create_web_page(title, content=""):
    """Create an HTML file"""
    path = os.path.expanduser(f"~/Desktop/{title}.html")
    html = f'''<!DOCTYPE html>
<html>
<head>
<title>{title}</title>
<style>
body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: auto; }}
h1 {{ color: #333; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p>{content}</p>
</body>
</html>'''
    with open(path, 'w') as f:
        f.write(html)
    webbrowser.open(f"file://{path}")
    return f"Created and opened {title}.html on Desktop, sir."

def create_javascript_file(filename, code=""):
    path = os.path.expanduser(f"~/Desktop/{filename}")
    with open(path, 'w') as f:
        f.write(code or 'console.log("Hello from JARVIS");')
    return f"Created {filename} on Desktop, sir."

def install_pip_package(package):
    """Install a pip package"""
    result = subprocess.run(["pip3","install",package], capture_output=True, text=True)
    if result.returncode == 0:
        return f"Installed {package}, sir."
    return f"Failed to install {package}, sir."

def install_brew_package(package):
    """Install a Homebrew package"""
    if IS_MAC:
        result = subprocess.run(["brew","install",package], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Installed {package} via Homebrew, sir."
        return f"Failed to install {package}, sir."
    return "Only available on macOS."

def create_project(name, ptype="python"):
    base = os.path.expanduser("~/Desktop")
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    if ptype == "python":
        with open(os.path.join(d,"main.py"),'w') as f: f.write(f'#!/usr/bin/env python3\n\nprint("Hello from {name}")\n')
        with open(os.path.join(d,"README.md"),'w') as f: f.write(f"# {name}\n\nCreated by JARVIS\n")
    elif ptype == "web":
        with open(os.path.join(d,"index.html"),'w') as f: f.write(f'<!DOCTYPE html>\n<html><head><title>{name}</title></head><body><h1>{name}</h1></body></html>\n')
        with open(os.path.join(d,"style.css"),'w') as f: f.write("body { font-family: Arial; }\n")
        with open(os.path.join(d,"script.js"),'w') as f: f.write("// JavaScript\n")
    elif ptype == "flask":
        with open(os.path.join(d,"app.py"),'w') as f: f.write(f'from flask import Flask\napp = Flask(__name__)\n\n@app.route("/")\ndef home():\n    return "Hello from {name}"\n\nif __name__ == "__main__":\n    app.run(port=5000)\n')
        with open(os.path.join(d,"requirements.txt"),'w') as f: f.write("flask\n")
    return f"Created {ptype} project '{name}' on Desktop, sir."

# ===== CLAUDE AI INTEGRATION =====
def ask_claude(prompt):
    """Send a prompt to Claude AI via API"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "Claude API key not configured, sir. Set ANTHROPIC_API_KEY environment variable."
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 500, "messages": [{"role": "user", "content": prompt}]},
            timeout=30)
        data = resp.json()
        return data.get("content", [{}])[0].get("text", "No response from Claude, sir.")
    except Exception as e:
        return f"Claude API error: {str(e)}"

# ===== API SKILLS =====
def get_weather(city="Lahore"):
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1", timeout=10).json()
        if geo.get("results"):
            lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
            w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m", timeout=10).json()
            c = w.get("current",{})
            cond = {0:"clear",1:"mainly clear",2:"partly cloudy",3:"overcast",45:"foggy",51:"light drizzle",53:"drizzle",61:"light rain",63:"rain",65:"heavy rain",71:"light snow",73:"snow",80:"showers",95:"thunderstorm"}
            return f"Weather in {city}: {c.get('temperature_2m',0)}C, {cond.get(c.get('weather_code',0),'unknown')}, humidity {c.get('relative_humidity_2m',0)}%, wind {c.get('wind_speed_10m',0)} km/h"
        return f"City not found: {city}"
    except:
        return "Weather unavailable, sir."

def get_news():
    try:
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        ids = resp.json()[:5]
        news = []
        for sid in ids:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if s: news.append(s.get('title','Unknown'))
        return "Top news: " + ". ".join(news)
    except:
        return "News unavailable, sir."

def get_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5).json()
        return f"{r['setup']} ... {r['punchline']}"
    except:
        return "Why don't programmers like nature? Too many bugs."

def get_quote():
    try:
        r = requests.get("https://api.quotable.io/random", timeout=5).json()
        return f"{r['content']} — {r['author']}"
    except:
        return "The only way to do great work is to love what you do. — Steve Jobs"

def search_wikipedia(query):
    try:
        sr = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srprop=none&limit=1", timeout=10)
        results = sr.json().get("query",{}).get("search",[])
        if results:
            title = results[0]["title"]
            r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ','_')}", timeout=10)
            if r.status_code == 200: return r.json().get("extract","No info, sir.")
        return f"No article for {query}, sir."
    except:
        return "Wikipedia unavailable, sir."

def get_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=10).json()
        return f"IP: {r.get('ip')} | {r.get('city')}, {r.get('country_name')} | ISP: {r.get('org')}"
    except:
        return "IP info unavailable, sir."

def get_crypto(coin="bitcoin"):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd", timeout=10).json()
        return f"{coin.capitalize()}: ${r.get(coin,{}).get('usd',0):,.2f} USD, sir."
    except:
        return "Crypto price unavailable, sir."

def get_time_in_tz(tz_name):
    try:
        from zoneinfo import ZoneInfo
        now = datetime.datetime.now(ZoneInfo(tz_name))
        return f"It's {now.strftime('%I:%M %p')} in {tz_name}, sir."
    except:
        return f"Timezone {tz_name} not found, sir."

def get_definition(word):
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            return f"{word}: {d[0]['meanings'][0]['definitions'][0]['definition']}"
        return f"No definition for {word}, sir."
    except:
        return "Dictionary unavailable, sir."

def get_trivia():
    try:
        r = requests.get("https://opentdb.com/api.php?amount=1&type=multiple", timeout=10).json()
        q = r["results"][0]
        return f"Trivia: {q['question']} | Answer: {q['correct_answer']}"
    except:
        return "Trivia unavailable, sir."

def web_search(query):
    """Search the web using DuckDuckGo"""
    try:
        r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1", timeout=10)
        data = r.json()
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            topics = data["RelatedTopics"][:3]
            results = [t.get("Text","") for t in topics if isinstance(t, dict) and "Text" in t]
            return " | ".join(results) if results else f"No results for {query}, sir."
        return f"No results for {query}, sir."
    except:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Opened web search for {query}, sir."

# ===== COMMAND PROCESSOR =====
def process_command(command):
    cmd = command.lower().strip()
    response = {"action": "speak", "text": "", "data": None}

    MAC_APPS = ["safari","notes","mail","music","messages","facetime","calendar","reminders","maps","photos","preview","calculator","terminal","finder","settings","system settings","app store","contacts","textedit","stickies","activity monitor"]
    WEBSITE_MAP = {"youtube":"youtube.com","google":"google.com","facebook":"facebook.com","twitter":"twitter.com","github":"github.com","gmail":"gmail.com","whatsapp":"web.whatsapp.com","instagram":"instagram.com","linkedin":"linkedin.com","spotify":"open.spotify.com","netflix":"netflix.com","amazon":"amazon.com","chatgpt":"chat.openai.com","base44":"app.base44.com","reddit":"reddit.com","wikipedia":"wikipedia.org","claude":"claude.ai","midjourney":"midjourney.com"}
    TZ_MAP = {"london":"Europe/London","new york":"America/New_York","tokyo":"Asia/Tokyo","dubai":"Asia/Dubai","karachi":"Asia/Karachi","lahore":"Asia/Karachi","paris":"Europe/Paris","sydney":"Australia/Sydney","singapore":"Asia/Singapore","los angeles":"America/Los_Angeles","toronto":"America/Toronto"}

    # Greetings
    if any(w in cmd for w in ["hello jarvis","hi jarvis","hey jarvis","jarvis are you there","jarvis you there","good morning","good evening"]):
        response["text"] = "Yes sir, JARVIS is here. How may I assist you?"
    elif "how are you" in cmd:
        response["text"] = "All systems operational, sir. Ready to assist."

    # Time / Date
    elif "time" in cmd and ("what" in cmd or "tell" in cmd or cmd == "time"):
        response["text"] = f"It's {datetime.datetime.now().strftime('%I:%M %p')}, sir."
    elif "date" in cmd or ("today" in cmd and "what" in cmd):
        response["text"] = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, sir."

    # Weather
    elif "weather" in cmd:
        city = "Lahore"
        if " in " in cmd:
            parts = cmd.split(" in ")
            if len(parts) > 1: city = parts[-1]
        response["text"] = get_weather(city)

    # News
    elif "news" in cmd:
        response["text"] = get_news()

    # Claude AI
    elif cmd.startswith("ask claude") or cmd.startswith("claude "):
        prompt = cmd.replace("ask claude ", "").replace("claude ", "")
        response["text"] = ask_claude(prompt)

    # Web search
    elif cmd.startswith("search ") and "github" not in cmd:
        query = cmd.replace("search ", "")
        response["text"] = web_search(query)

    # GitHub search
    elif cmd.startswith("github search") or cmd.startswith("search github"):
        query = cmd.replace("github search ", "").replace("search github ", "").replace("search github for ", "")
        response["text"] = github_search(query)

    # GitHub install
    elif cmd.startswith("install ") and "github" in cmd or cmd.startswith("github install"):
        url = cmd.replace("github install ", "").replace("install from github ", "").replace("install ", "").strip()
        if "http" in url:
            response["text"] = github_install(url)
        else:
            response["text"] = "Please provide a full GitHub URL, sir. Example: install https://github.com/user/repo"

    # GitHub clone
    elif cmd.startswith("clone ") or cmd.startswith("git clone"):
        url = cmd.replace("git clone ", "").replace("clone ", "").strip()
        if "http" in url:
            response["text"] = git_clone(url)
        else:
            response["text"] = "Please provide a full GitHub URL, sir."

    # Git push
    elif "git push" in cmd or "commit and push" in cmd or "push to github" in cmd:
        msg = "Update"
        if "message" in cmd:
            parts = cmd.split("message")
            if len(parts) > 1: msg = parts[-1].strip()
        response["text"] = git_push(msg)

    # Git init
    elif cmd.startswith("git init") or cmd.startswith("create repo"):
        name = cmd.replace("git init ", "").replace("create repo ", "").strip()
        response["text"] = git_init_repo(name if name else "new_repo")

    # Download from GitHub
    elif cmd.startswith("download ") and "github" in cmd:
        parts = cmd.replace("download ", "").split()
        if len(parts) >= 2:
            response["text"] = download_github_file(parts[0], parts[1])
        else:
            response["text"] = "Say: download [url] [filename], sir."

    # VS Code
    elif "vs code" in cmd or "vscode" in cmd or "visual studio" in cmd:
        if "open" in cmd or "launch" in cmd or "start" in cmd:
            response["text"] = open_vscode()

    # GitHub Desktop
    elif "github desktop" in cmd:
        response["text"] = open_github_desktop()

    # Terminal
    elif "open terminal" in cmd or "launch terminal" in cmd:
        response["text"] = open_terminal()
    elif cmd.startswith("run ") or cmd.startswith("execute "):
        response["text"] = run_terminal_command(cmd.replace("run ", "").replace("execute ", ""))

    # Install pip package
    elif cmd.startswith("pip install") or cmd.startswith("install pip"):
        pkg = cmd.replace("pip install ", "").replace("install pip ", "").strip()
        response["text"] = install_pip_package(pkg)

    # Install brew package
    elif cmd.startswith("brew install") or cmd.startswith("install brew"):
        pkg = cmd.replace("brew install ", "").replace("install brew ", "").strip()
        response["text"] = install_brew_package(pkg)

    # Run Python code
    elif cmd.startswith("python ") and "code" not in cmd:
        code = cmd.replace("python ", "")
        response["text"] = run_python(code)

    # Run Python file
    elif cmd.startswith("run file ") or cmd.startswith("run python file"):
        fname = cmd.replace("run file ", "").replace("run python file ", "").strip()
        response["text"] = run_python_file(fname)

    # Create Python file
    elif cmd.startswith("create python") or cmd.startswith("new python file"):
        parts = cmd.replace("create python file ", "").replace("create python ", "").replace("new python file ", "").split(" ", 1)
        fname = parts[0] if parts[0].endswith(".py") else parts[0] + ".py"
        code = parts[1] if len(parts) > 1 else ""
        response["text"] = create_python_file(fname, code)

    # Create web page
    elif cmd.startswith("create web page") or cmd.startswith("create html") or cmd.startswith("new website"):
        parts = cmd.replace("create web page ", "").replace("create html ", "").replace("new website ", "").split(" ", 1)
        title = parts[0]
        content = parts[1] if len(parts) > 1 else "Created by JARVIS"
        response["text"] = create_web_page(title, content)

    # Create JS file
    elif cmd.startswith("create javascript") or cmd.startswith("new js file"):
        parts = cmd.replace("create javascript file ", "").replace("create javascript ", "").replace("new js file ", "").split(" ", 1)
        fname = parts[0] if parts[0].endswith(".js") else parts[0] + ".js"
        code = parts[1] if len(parts) > 1 else ""
        response["text"] = create_javascript_file(fname, code)

    # Create project
    elif cmd.startswith("create project") or cmd.startswith("new project"):
        parts = cmd.replace("create project ", "").replace("new project ", "").split()
        name = parts[0] if parts else "new_project"
        ptype = "python"
        if "web" in cmd or "html" in cmd: ptype = "web"
        elif "flask" in cmd: ptype = "flask"
        response["text"] = create_project(name, ptype)
        if IS_MAC:
            time.sleep(1)
            open_vscode(os.path.expanduser(f"~/Desktop/{name}"))

    # Open website or app
    elif cmd.startswith("open ") or cmd.startswith("go to "):
        site = cmd.replace("open ", "").replace("go to ", "")
        if site.lower() in MAC_APPS:
            response["text"] = open_app(site.title())
        elif "." in site or site.lower() in WEBSITE_MAP:
            url = WEBSITE_MAP.get(site.lower(), site if "." in site else site + ".com")
            if not url.startswith("http"): url = "https://" + url
            webbrowser.open(url)
            response["text"] = f"Opening {url}, sir."
        else:
            response["text"] = open_app(site.title())

    # Close app
    elif cmd.startswith("close ") or cmd.startswith("quit "):
        response["text"] = close_app(cmd.replace("close ", "").replace("quit ", "").title())

    # Running apps
    elif "running" in cmd and "app" in cmd:
        response["text"] = list_running_apps()

    # Type text
    elif cmd.startswith("type "):
        response["text"] = type_in_app(cmd.replace("type ", ""))

    # Press key
    elif cmd.startswith("press "):
        response["text"] = press_key(cmd.replace("press ", ""))

    # Copy paste
    elif "copy paste" in cmd or cmd == "paste":
        response["text"] = copy_paste()

    # Volume
    elif "volume" in cmd:
        for w in cmd.split():
            if w.isdigit():
                response["text"] = set_volume(w)
                break
        else:
            if "up" in cmd:
                if IS_MAC: applescript("set volume output volume (output volume of (get volume settings)) + 10")
                response["text"] = "Volume up, sir."
            elif "down" in cmd:
                if IS_MAC: applescript("set volume output volume (output volume of (get volume settings)) - 10")
                response["text"] = "Volume down, sir."
            elif "mute" in cmd:
                response["text"] = set_volume(0)
            else:
                response["text"] = get_volume()

    # Screenshot
    elif "screenshot" in cmd:
        response["text"] = take_screenshot()

    # System info
    elif "system" in cmd and ("info" in cmd or "status" in cmd):
        response["text"] = "Retrieving system info, sir."
        response["data"] = {"type": "system", "info": system_info()}

    # IP
    elif "ip address" in cmd or "my ip" in cmd:
        response["text"] = get_ip()

    # Wikipedia
    elif "what is" in cmd or "who is" in cmd or "tell me about" in cmd or "search wikipedia" in cmd:
        query = cmd.replace("what is ","").replace("who is ","").replace("tell me about ","").replace("search wikipedia for ","").replace("search wikipedia ","")
        response["text"] = search_wikipedia(query)

    # Dictionary
    elif "define" in cmd or "definition" in cmd:
        response["text"] = get_definition(cmd.replace("define ","").replace("definition of ","").replace("definition ",""))

    # Joke / Quote / Trivia
    elif "joke" in cmd:
        response["text"] = get_joke()
    elif "quote" in cmd:
        response["text"] = get_quote()
    elif "trivia" in cmd:
        response["text"] = get_trivia()

    # Crypto
    elif "bitcoin" in cmd or "ethereum" in cmd or "crypto" in cmd or "doge" in cmd:
        coin = "bitcoin"
        if "ethereum" in cmd or "ether" in cmd: coin = "ethereum"
        elif "doge" in cmd: coin = "dogecoin"
        response["text"] = get_crypto(coin)

    # Time in timezone
    elif "time in" in cmd:
        tz = cmd.replace("time in ","").replace("what time is it in ","").strip()
        response["text"] = get_time_in_tz(TZ_MAP.get(tz, tz))

    # Play music
    elif "play" in cmd and ("music" in cmd or "song" in cmd):
        song = cmd.replace("play ","").replace("music","").replace("song","").strip()
        if song:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            response["text"] = f"Playing {song} on YouTube, sir."
        else:
            webbrowser.open("https://www.youtube.com/results?search_query=music")
            response["text"] = "Playing music, sir."

    # Folders
    elif cmd.startswith("open ") and any(f in cmd for f in ["desktop","documents","downloads","pictures","music","movies","applications","home folder"]):
        response["text"] = open_folder(cmd.replace("open ","").replace(" folder",""))

    # Note
    elif cmd.startswith("note ") or cmd.startswith("create note"):
        response["text"] = create_note("JARVIS Note", cmd.replace("note ","").replace("create note ",""))

    # Reminder
    elif cmd.startswith("remind ") or cmd.startswith("reminder "):
        response["text"] = create_reminder(cmd.replace("remind ","").replace("reminder ",""))

    # Lock / Sleep / Restart / Shutdown
    elif "lock" in cmd and "screen" in cmd or cmd == "lock":
        response["text"] = lock_screen()
    elif "sleep" in cmd and "mac" in cmd or cmd == "sleep":
        response["text"] = sleep_mac()
    elif "restart" in cmd:
        response["text"] = restart_mac()
    elif "shutdown" in cmd and "jarvis" not in cmd:
        response["text"] = shutdown_mac()

    # Empty trash
    elif "empty trash" in cmd or "clear trash" in cmd:
        response["text"] = empty_trash()

    # Calculate
    elif "calculate" in cmd or any(op in cmd for op in ["plus","minus","times","divided"]):
        expr = cmd.replace("calculate ","").replace("what is ","").replace("what's ","")
        expr = expr.replace("plus","+").replace("minus","-").replace("times","*").replace("divided by","/").replace("x","*")
        if all(c in "0123456789+-*/.() " for c in expr):
            try: response["text"] = f"Answer: {eval(expr)}, sir."
            except: response["text"] = "Couldn't calculate, sir."
        else:
            response["text"] = "Basic math only, sir."

    # Clear
    elif "clear" in cmd or "reset" in cmd:
        response["text"] = "Interface cleared, sir."
        response["data"] = {"type": "clear"}

    # Help
    elif "help" in cmd or "what can you do" in cmd:
        response["text"] = "I have 60+ skills, sir. Check the skills panel on the left."
        response["data"] = {"type": "help"}

    # Thank you
    elif "thank" in cmd:
        response["text"] = "Always a pleasure, sir."

    # Goodbye
    elif "goodbye" in cmd or "shut down jarvis" in cmd or "sign off" in cmd:
        response["text"] = "Goodbye, sir. JARVIS signing off."
        response["data"] = {"type": "shutdown_jarvis"}

    # Default - web search
    else:
        webbrowser.open(f"https://www.google.com/search?q={command}")
        response["text"] = f"I searched the web for {command}, sir."

    # Speak response via macOS
    jarvis_speak(response["text"])
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
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#000; color:#00aaff; font-family:'Helvetica Neue',Arial,sans-serif; overflow:hidden; height:100vh; display:flex; flex-direction:column; align-items:center; }
.header { position:fixed; top:0; width:100%; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; z-index:100; }
.logo { font-size:14px; letter-spacing:4px; color:#00aaff; opacity:0.7; }
.status { font-size:11px; }
.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; }
.status-listening .status-dot { background:#ffc800; animation:pulse 1s infinite; }
.status-thinking .status-dot { background:#9966ff; animation:pulse 0.5s infinite; }
.status-idle .status-dot { background:#00ff88; animation:pulse 2s infinite; }
.status-speaking .status-dot { background:#00aaff; animation:pulse 0.8s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.reactor { position:relative; width:280px; height:280px; margin-top:35px; display:flex; align-items:center; justify-content:center; }
.reactor-ring { position:absolute; border-radius:50%; }
.r1 { width:280px; height:280px; border:1px solid rgba(0,170,255,0.2); animation:spin 10s linear infinite; }
.r2 { width:220px; height:220px; border:2px solid rgba(0,170,255,0.3); animation:spin 7s linear infinite reverse; }
.r3 { width:160px; height:160px; border:1px solid rgba(0,170,255,0.4); animation:spin 5s linear infinite; }
.r4 { width:100px; height:100px; border:2px solid rgba(0,170,255,0.5); animation:spin 3s linear infinite reverse; }
.r-core { width:60px; height:60px; border-radius:50%; background:radial-gradient(circle,rgba(0,170,255,0.8),rgba(0,100,200,0.3),transparent); box-shadow:0 0 50px rgba(0,170,255,0.6); animation:corepulse 2s ease-in-out infinite; display:flex; align-items:center; justify-content:center; font-size:8px; color:#fff; letter-spacing:1px; }
@keyframes corepulse { 0%,100%{transform:scale(1;} 50%{transform:scale(1.1);} }
@keyframes spin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
.reactor-listening .r-core { background:radial-gradient(circle,rgba(255,200,0,0.8),rgba(255,100,0,0.3),transparent); box-shadow:0 0 70px rgba(255,200,0,0.6); }
.reactor-thinking .r-core { background:radial-gradient(circle,rgba(150,100,255,0.8),rgba(100,100,200,0.3),transparent); box-shadow:0 0 70px rgba(150,100,255,0.6); }
.reactor-speaking .r-core { background:radial-gradient(circle,rgba(0,170,255,0.9),rgba(0,100,200,0.4),transparent); box-shadow:0 0 80px rgba(0,170,255,0.8); }
.auto-mode { position:fixed; top:50px; right:20px; display:flex; align-items:center; gap:8px; z-index:100; }
.auto-toggle { width:44px; height:24px; border-radius:12px; background:rgba(0,170,255,0.2); border:1px solid rgba(0,170,255,0.4); cursor:pointer; position:relative; }
.auto-toggle.on { background:rgba(0,255,136,0.3); border-color:#00ff88; }
.auto-toggle .knob { width:18px; height:18px; border-radius:50%; background:#00aaff; position:absolute; top:2px; left:2px; transition:all 0.3s; }
.auto-toggle.on .knob { left:22px; background:#00ff88; }
.auto-label { font-size:11px; color:rgba(0,170,255,0.6); }
.skills-panel { position:fixed; top:45px; left:8px; width:195px; max-height:85vh; overflow-y:auto; padding:5px; }
.skills-title { font-size:10px; color:rgba(0,170,255,0.4); letter-spacing:2px; margin-bottom:6px; padding-left:4px; }
.skill-cat { font-size:9px; color:rgba(0,255,136,0.4); margin:8px 0 4px 4px; letter-spacing:1px; }
.skill-btn { padding:5px 10px; margin-bottom:3px; border-radius:14px; background:rgba(0,170,255,0.05); border:1px solid rgba(0,170,255,0.15); color:rgba(0,170,255,0.5); font-size:10px; cursor:pointer; transition:all 0.15s; }
.skill-btn:hover { background:rgba(0,170,255,0.15); border-color:rgba(0,170,255,0.4); color:#00aaff; }
.conversation { position:fixed; top:85px; right:20px; width:300px; max-height:50vh; overflow-y:auto; padding:5px; }
.msg { margin-bottom:8px; padding:8px 12px; border-radius:12px; font-size:12px; line-height:1.5; opacity:0; animation:fadeIn 0.3s forwards; }
@keyframes fadeIn { to{opacity:1;} }
.msg.user { background:rgba(0,170,255,0.1); border:1px solid rgba(0,170,255,0.2); text-align:right; margin-left:40px; }
.msg.jarvis { background:rgba(0,255,136,0.05); border:1px solid rgba(0,255,136,0.2); margin-right:40px; }
.msg .label { font-size:9px; color:rgba(255,255,255,0.3); margin-bottom:2px; }
.status-text { position:fixed; top:50%; left:50%; transform:translate(-50%,80px); font-size:12px; color:rgba(0,170,255,0.6); letter-spacing:2px; text-align:center; width:300px; }
.controls { position:fixed; bottom:0; width:100%; padding:15px; display:flex; flex-direction:column; align-items:center; gap:8px; }
.mic-btn { width:50px; height:50px; border-radius:50%; border:2px solid #00aaff; background:rgba(0,170,255,0.1); color:#00aaff; cursor:pointer; font-size:20px; display:flex; align-items:center; justify-content:center; transition:all 0.3s; }
.mic-btn:hover { background:rgba(0,170,255,0.3); box-shadow:0 0 20px rgba(0,170,255,0.5); }
.mic-btn.listening { background:rgba(255,200,0,0.3); border-color:#ffc800; box-shadow:0 0 30px rgba(255,200,0,0.6); animation:pulse 1s infinite; }
.mic-btn.auto { background:rgba(0,255,136,0.2); border-color:#00ff88; }
.command-bar { position:relative; width:80%; max-width:600px; }
.command-input { width:100%; padding:10px 40px 10px 18px; border-radius:25px; background:rgba(0,170,255,0.05); border:1px solid rgba(0,170,255,0.3); color:#00aaff; font-size:13px; outline:none; font-family:'Helvetica Neue',Arial; }
.command-input:focus { border-color:rgba(0,170,255,0.6); box-shadow:0 0 15px rgba(0,170,255,0.2); }
.command-input::placeholder { color:rgba(0,170,255,0.3); }
.send-btn { position:absolute; right:12px; top:50%; transform:translateY(-50%); background:none; border:none; color:#00aaff; cursor:pointer; font-size:16px; }
.data-display { position:fixed; bottom:100px; left:50%; transform:translateX(-50%); width:90%; max-width:500px; max-height:120px; overflow-y:auto; display:none; }
.data-display.active { display:block; }
.data-card { background:rgba(0,170,255,0.05); border:1px solid rgba(0,170,255,0.2); border-radius:8px; padding:12px; margin-top:4px; font-size:11px; }
.data-card h4 { color:#00aaff; margin-bottom:6px; font-size:12px; }
.data-card pre { color:rgba(0,255,136,0.7); white-space:pre-wrap; font-size:10px; }
</style>
</head>
<body>

<div class="header">
    <div class="logo">J.A.R.V.I.S v4.0</div>
    <div class="status status-idle" id="statusBar"><span class="status-dot"></span><span id="statusText">ONLINE</span></div>
</div>

<div class="auto-mode">
    <span class="auto-label">AUTO-LISTEN</span>
    <div class="auto-toggle on" id="autoToggle" onclick="toggleAutoListen()"><div class="knob"></div></div>
</div>

<div class="skills-panel">
    <div class="skills-title">SKILLS (60+)</div>
    <div class="skill-cat">CODE & DEV</div>
    <div class="skill-btn" onclick="sendCmd('open vs code')">VS Code</div>
    <div class="skill-btn" onclick="sendCmd('open github desktop')">GitHub Desktop</div>
    <div class="skill-btn" onclick="sendCmd('create project myapp python')">New Python Project</div>
    <div class="skill-btn" onclick="sendCmd('create project myweb web')">New Web Project</div>
    <div class="skill-btn" onclick="sendCmd('create project myapi flask')">New Flask Project</div>
    <div class="skill-btn" onclick="sendCmd('create web page test Hello')">Create HTML</div>
    <div class="skill-btn" onclick="sendCmd('create python test.py print hello')">Create Python</div>
    <div class="skill-btn" onclick="sendCmd('python print(2+2)')">Run Python Code</div>
    <div class="skill-btn" onclick="sendCmd('open terminal')">Open Terminal</div>
    <div class="skill-btn" onclick="sendCmd('pip install requests')">Install Package</div>
    <div class="skill-cat">GITHUB</div>
    <div class="skill-btn" onclick="sendCmd('github search flask app')">Search GitHub</div>
    <div class="skill-btn" onclick="sendCmd('commit and push')">Git Push</div>
    <div class="skill-btn" onclick="sendCmd('git init myrepo')">Git Init</div>
    <div class="skill-cat">AI</div>
    <div class="skill-btn" onclick="sendCmd('ask claude what is AI')">Ask Claude</div>
    <div class="skill-cat">DESKTOP</div>
    <div class="skill-btn" onclick="sendCmd('open safari')">Safari</div>
    <div class="skill-btn" onclick="sendCmd('open notes')">Notes</div>
    <div class="skill-btn" onclick="sendCmd('open music')">Music</div>
    <div class="skill-btn" onclick="sendCmd('open mail')">Mail</div>
    <div class="skill-btn" onclick="sendCmd('open finder')">Finder</div>
    <div class="skill-btn" onclick="sendCmd('open calculator')">Calculator</div>
    <div class="skill-btn" onclick="sendCmd('open settings')">Settings</div>
    <div class="skill-btn" onclick="sendCmd('close safari')">Close App</div>
    <div class="skill-btn" onclick="sendCmd('running apps')">Running Apps</div>
    <div class="skill-btn" onclick="sendCmd('screenshot')">Screenshot</div>
    <div class="skill-cat">SYSTEM</div>
    <div class="skill-btn" onclick="sendCmd('volume up')">Volume Up</div>
    <div class="skill-btn" onclick="sendCmd('volume down')">Volume Down</div>
    <div class="skill-btn" onclick="sendCmd('system info')">System Info</div>
    <div class="skill-btn" onclick="sendCmd('lock screen')">Lock Mac</div>
    <div class="skill-btn" onclick="sendCmd('sleep')">Sleep Mac</div>
    <div class="skill-btn" onclick="sendCmd('empty trash')">Empty Trash</div>
    <div class="skill-cat">FOLDERS</div>
    <div class="skill-btn" onclick="sendCmd('open desktop')">Desktop</div>
    <div class="skill-btn" onclick="sendCmd('open documents')">Documents</div>
    <div class="skill-btn" onclick="sendCmd('open downloads')">Downloads</div>
    <div class="skill-cat">KNOWLEDGE</div>
    <div class="skill-btn" onclick="sendCmd('what is artificial intelligence')">Wikipedia</div>
    <div class="skill-btn" onclick="sendCmd('define computer')">Dictionary</div>
    <div class="skill-btn" onclick="sendCmd('search latest AI news')">Web Search</div>
    <div class="skill-btn" onclick="sendCmd('joke')">Joke</div>
    <div class="skill-btn" onclick="sendCmd('quote')">Quote</div>
    <div class="skill-btn" onclick="sendCmd('trivia')">Trivia</div>
    <div class="skill-cat">DAILY</div>
    <div class="skill-btn" onclick="sendCmd('what time is it')">Time</div>
    <div class="skill-btn" onclick="sendCmd('what is the date')">Date</div>
    <div class="skill-btn" onclick="sendCmd('weather in Lahore')">Weather</div>
    <div class="skill-btn" onclick="sendCmd('news')">News</div>
    <div class="skill-btn" onclick="sendCmd('note buy groceries')">Note</div>
    <div class="skill-btn" onclick="sendCmd('remind call mom')">Reminder</div>
    <div class="skill-cat">WEB</div>
    <div class="skill-btn" onclick="sendCmd('open youtube')">YouTube</div>
    <div class="skill-btn" onclick="sendCmd('open google')">Google</div>
    <div class="skill-btn" onclick="sendCmd('open chatgpt')">ChatGPT</div>
    <div class="skill-btn" onclick="sendCmd('open claude')">Claude</div>
    <div class="skill-btn" onclick="sendCmd('play music')">Play Music</div>
    <div class="skill-btn" onclick="sendCmd('bitcoin price')">Bitcoin</div>
    <div class="skill-btn" onclick="sendCmd('my ip address')">IP Address</div>
    <div class="skill-btn" onclick="sendCmd('time in london')">Time London</div>
    <div class="skill-btn" onclick="sendCmd('time in new york')">Time NY</div>
</div>

<div class="reactor" id="reactor">
    <div class="reactor-ring r1"></div>
    <div class="reactor-ring r2"></div>
    <div class="reactor-ring r3"></div>
    <div class="reactor-ring r4"></div>
    <div class="r-core" id="core">JARVIS</div>
</div>

<div class="status-text" id="bootText">Say "JARVIS" then your command, sir</div>
<div class="conversation" id="conversation"></div>
<div class="data-display" id="dataDisplay"></div>

<div class="controls">
    <button class="mic-btn auto" id="micBtn" onclick="toggleVoice()">&#127908;</button>
    <div class="command-bar">
        <input type="text" class="command-input" id="commandInput" placeholder="Type or say a command..." onkeypress="if(event.key==='Enter') sendInput()">
        <button class="send-btn" onclick="sendInput()">&#9654;</button>
    </div>
</div>

<script>
let recognition=null,isListening=false,autoListen=true,wakeWordDetected=false;
if('webkitSpeechRecognition' in window||'SpeechRecognition' in window){
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    recognition=new SR();recognition.continuous=true;recognition.interimResults=true;recognition.lang='en-US';
    recognition.onresult=(e)=>{
        let t='',f=false;
        for(let i=e.resultIndex;i<e.results.length;i++){t+=e.results[i][0].transcript;if(e.results[i].isFinal)f=true;}
        t=t.toLowerCase().trim();
        if(autoListen){
            if(t.includes('jarvis')||t.includes('travis')||t.includes('jeff')){
                wakeWordDetected=true;setReactorState('listening');
                let c=t.replace(/.*jarvis[, ]*/,'').replace(/.*travis[, ]*/,'').replace(/.*jeff[, ]*/,'').trim();
                if(c&&f){addMessage('user',c);sendToJarvis(c);wakeWordDetected=false;}
                else if(c){document.getElementById('commandInput').value=c;}
            }else if(wakeWordDetected&&t){
                document.getElementById('commandInput').value=t;
                if(f){addMessage('user',t);sendToJarvis(t);wakeWordDetected=false;}
            }
        }else{
            document.getElementById('commandInput').value=t;
            if(f&&t) sendInput();
        }
    };
    recognition.onerror=(e)=>{if(autoListen&&e.error!=='not-allowed')setTimeout(startAutoListening,1000);};
    recognition.onend=()=>{isListening=false;document.getElementById('micBtn').classList.remove('listening');if(autoListen)setTimeout(startAutoListening,500);else setReactorState('idle');};
}
function startAutoListening(){if(!recognition||isListening)return;try{recognition.start();isListening=true;document.getElementById('micBtn').classList.add('listening');setReactorState('idle');}catch(e){}}
function toggleAutoListen(){autoListen=!autoListen;document.getElementById('autoToggle').classList.toggle('on',autoListen);if(autoListen)startAutoListening();else if(isListening)recognition.stop();}
function toggleVoice(){if(!recognition){addMessage('jarvis','Voice needs Safari or Chrome, sir.');return;}autoListen=false;document.getElementById('autoToggle').classList.remove('on');if(isListening){recognition.stop();}else{try{recognition.start();isListening=true;document.getElementById('micBtn').classList.add('listening');setReactorState('listening');}catch(e){}}}
function setReactorState(s){const r=document.getElementById('reactor'),c=document.getElementById('core'),b=document.getElementById('bootText'),sb=document.getElementById('statusBar');
r.classList.remove('reactor-listening','reactor-thinking','reactor-speaking');sb.classList.remove('status-idle','status-listening','status-thinking','status-speaking');
if(s==='listening'){r.classList.add('reactor-listening');sb.classList.add('status-listening');c.textContent='LISTEN';b.textContent='I am listening, sir...';document.getElementById('statusText').textContent='LISTENING';}
else if(s==='thinking'){r.classList.add('reactor-thinking');sb.classList.add('status-thinking');c.textContent='PROC';b.textContent='Processing, sir...';document.getElementById('statusText').textContent='PROCESSING';}
else if(s==='speaking'){r.classList.add('reactor-speaking');sb.classList.add('status-speaking');c.textContent='SPEAK';b.textContent='Speaking, sir...';document.getElementById('statusText').textContent='SPEAKING';}
else{sb.classList.add('status-idle');c.textContent='JARVIS';b.textContent='Say "JARVIS" then your command, sir';document.getElementById('statusText').textContent=autoListen?'AUTO-LISTEN':'ONLINE';}}
function sendCmd(c){addMessage('user',c);sendToJarvis(c);}
function sendInput(){const i=document.getElementById('commandInput');const c=i.value.trim();if(!c)return;i.value='';addMessage('user',c);sendToJarvis(c);}
function sendToJarvis(command){
    setReactorState('thinking');
    fetch('/api/command',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:command})})
    .then(r=>r.json()).then(data=>{
        setReactorState('speaking');addMessage('jarvis',data.text);
        if(data.data)displayData(data.data);
        if('speechSynthesis' in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(data.text);u.rate=0.95;u.pitch=0.85;u.volume=0.8;const v=speechSynthesis.getVoices();const p=v.find(v=>v.name.includes('Daniel')||v.name.includes('Arthur'));if(p)u.voice=p;u.onend=()=>setReactorState('idle');speechSynthesis.speak(u);}else setTimeout(()=>setReactorState('idle'),2000);
    }).catch(e=>{setReactorState('idle');addMessage('jarvis','Connection error, sir.');});
}
function addMessage(s,t){const c=document.getElementById('conversation');const m=document.createElement('div');m.className='msg '+s;m.innerHTML='<div class="label">'+(s==='user'?'YOU':'JARVIS')+'</div>'+t;c.appendChild(m);c.scrollTop=c.scrollHeight;}
function displayData(d){const e=document.getElementById('dataDisplay');
if(d.type==='system'){e.innerHTML='<div class="data-card"><h4>SYSTEM INFO</h4><pre>'+d.info+'</pre></div>';e.classList.add('active');}
else if(d.type==='clear'){document.getElementById('conversation').innerHTML='';e.classList.remove('active');}
else if(d.type==='shutdown_jarvis')setTimeout(()=>window.close(),3000);
}
setTimeout(()=>{addMessage('jarvis','JARVIS v4.0 online, sir. 60+ skills loaded. Auto-listening is ON. Just say JARVIS followed by your command.');setTimeout(startAutoListening,1500);},800);
if('speechSynthesis' in window){speechSynthesis.onvoiceschanged=()=>{};speechSynthesis.getVoices();}
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
    print("=" * 55)
    print("  J.A.R.V.I.S v4.0 — AI Assistant")
    print("  Voice: macOS native 'say' (Daniel voice)")
    print("  60+ Skills: Code, GitHub, Claude, Desktop, Web")
    print("  Auto-listening: ON")
    print("  Say 'JARVIS' then your command")
    print("  Browser: http://localhost:7654")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    webbrowser.open("http://localhost:7654")
    app.run(host='0.0.0.0', port=7654, debug=False)
