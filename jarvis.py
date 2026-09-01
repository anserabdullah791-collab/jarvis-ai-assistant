#!/usr/bin/env python3
"""
JARVIS v3.0 — Complete AI Assistant
- macOS native voice (say command) — ALWAYS speaks
- Auto-listening wake word ("Jarvis")
- Real desktop control (AppleScript)
- GitHub + VS Code + Terminal integration
- 50+ skills
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
import shutil

app = Flask(__name__)

IS_MAC = platform.system() == "Darwin"

# ===== NATIVE VOICE OUTPUT (macOS 'say' command) =====

def jarvis_speak(text):
    """Speak using macOS native 'say' command — always works on Mac"""
    if IS_MAC:
        # Clean text for speech
        clean = text.replace(" sir", "").replace("Sir, ", "").replace("\n", " ")
        # Use a good voice — Daniel is the JARVIS-like British voice on macOS
        # Try different voices, fall back to default
        try:
            subprocess.Popen(["say", "-v", "Daniel", "-r", "180", clean],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            subprocess.Popen(["say", "-r", "180", clean],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return text

# ===== MAC AUTOMATION =====

def applescript(script):
    """Run AppleScript — controls any Mac app"""
    try:
        result = subprocess.run(["osascript", "-e", script],
                              capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

def open_app(app_name):
    if IS_MAC:
        # Try to open and activate
        r = applescript(f'tell application "{app_name}" to activate')
        if "Error" in r:
            # Try with 'open -a'
            subprocess.Popen(["open", "-a", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {app_name}, sir."
    return "Only available on macOS."

def close_app(app_name):
    if IS_MAC:
        applescript(f'tell application "{app_name}" to quit')
        return f"Closing {app_name}, sir."
    return "Only available on macOS."

def open_vscode(path=None):
    """Open VS Code"""
    if IS_MAC:
        if path:
            subprocess.Popen(["code", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening VS Code with {path}, sir."
        else:
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
        applescript('tell application "System Events" to keystroke "n" using command down')
        return "Opening Terminal, sir."
    return "Only available on macOS."

def run_terminal_command(cmd):
    """Run a command in Terminal"""
    if IS_MAC:
        script = f'''
        tell application "Terminal"
            activate
            do script "{cmd}"
        end tell
        '''
        applescript(script)
        return f"Running command in Terminal: {cmd}"
    return "Only available on macOS."

def create_project(name, project_type="python"):
    """Create a new project folder with structure"""
    base = os.path.expanduser("~/Desktop")
    project_dir = os.path.join(base, name)
    os.makedirs(project_dir, exist_ok=True)
    
    if project_type == "python":
        with open(os.path.join(project_dir, "main.py"), "w") as f:
            f.write(f'#!/usr/bin/env python3\n\nprint("Hello from {name}")\n')
        with open(os.path.join(project_dir, "README.md"), "w") as f:
            f.write(f"# {name}\n\nCreated by JARVIS\n")
    elif project_type == "web":
        with open(os.path.join(project_dir, "index.html"), "w") as f:
            f.write(f'<!DOCTYPE html>\n<html>\n<head><title>{name}</title>\n</head>\n<body>\n<h1>{name}</h1>\n</body>\n</html>\n')
        with open(os.path.join(project_dir, "style.css"), "w") as f:
            f.write("body { font-family: Arial; }\n")
        with open(os.path.join(project_dir, "script.js"), "w") as f:
            f.write("// JavaScript\n")
    
    return f"Created {project_type} project '{name}' on your Desktop, sir."

def git_clone(repo_url):
    """Clone a git repo"""
    if IS_MAC:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target = os.path.expanduser(f"~/Desktop/{repo_name}")
        subprocess.run(["git", "clone", repo_url, target], capture_output=True)
        return f"Cloned {repo_name} to your Desktop, sir."
    return "Only available on macOS."

def git_commit_push(message="Update"):
    """Git add, commit, and push"""
    if IS_MAC:
        run_terminal_command(f"git add . && git commit -m '{message}' && git push")
        return f"Committing and pushing changes, sir."
    return "Only available on macOS."

def type_in_app(text):
    if IS_MAC:
        # Escape quotes
        safe_text = text.replace('"', '\\"')
        applescript(f'tell application "System Events" to keystroke "{safe_text}"')
        return f"Typed: {text}"
    return "Only available on macOS."

def press_key(key):
    if IS_MAC:
        key_map = {
            "enter": "return", "return": "return", "tab": "tab",
            "space": "space", "escape": "escape", "esc": "escape",
            "delete": "delete", "backspace": "delete",
            "up": "arrow up", "down": "arrow down",
            "left": "arrow left", "right": "arrow right",
            "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
            "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
            "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12"
        }
        mac_key = key_map.get(key.lower(), key.lower())
        applescript(f'tell application "System Events" to keystroke "{mac_key}"')
        return f"Pressed {key}"
    return "Only available on macOS."

def press_hotkey(*keys):
    """Press keyboard shortcut like Cmd+C"""
    if IS_MAC:
        key_names = {
            "command": "command down", "cmd": "command down",
            "shift": "shift down", "control": "control down",
            "ctrl": "control down", "option": "option down", "alt": "option down"
        }
        modifiers = [key_names.get(k.lower(), k.lower()) for k in keys[:-1]]
        last_key = keys[-1]
        mod_str = " using {" + ", ".join(modifiers) + "}" if modifiers else ""
        applescript(f'tell application "System Events" to keystroke "{last_key}"{mod_str}')
        return f"Pressed {'+'.join(keys)}"
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
        result = applescript("output volume of (get volume settings)")
        return f"Current volume is {result}%, sir."
    return "Only available on macOS."

def open_folder(folder_name):
    if IS_MAC:
        paths = {
            "desktop": "~/Desktop", "documents": "~/Documents",
            "downloads": "~/Downloads", "pictures": "~/Pictures",
            "music": "~/Music", "movies": "~/Movies",
            "applications": "/Applications", "home": "~"
        }
        path = paths.get(folder_name.lower(), folder_name)
        subprocess.Popen(["open", os.path.expanduser(path)])
        return f"Opening {folder_name}, sir."
    return "Only available on macOS."

def create_note(title, content):
    if IS_MAC:
        safe_title = title.replace('"', '\\"')
        safe_content = content.replace('"', '\\"')
        applescript(f'''
        tell application "Notes"
            tell account "iCloud"
                make new note with properties {{name:"{safe_title}", body:"{safe_content}"}}
            end tell
        end tell
        ''')
        return f"Note '{title}' created, sir."
    return "Only available on macOS."

def create_reminder(text):
    if IS_MAC:
        safe = text.replace('"', '\\"')
        applescript(f'tell application "Reminders" to make new reminder with properties {{name:"{safe}"}}')
        return f"Reminder added: {text}"
    return "Only available on macOS."

def send_imessage(phone, message_text):
    if IS_MAC:
        safe_phone = phone.replace('"', '\\"')
        safe_msg = message_text.replace('"', '\\"')
        applescript(f'''
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant "{safe_phone}" of targetService
            send "{safe_msg}" to targetBuddy
        end tell
        ''')
        return f"Message sent to {phone}, sir."
    return "Only available on macOS."

def send_email(to, subject, body):
    if IS_MAC:
        safe_to = to.replace('"', '\\"')
        safe_subj = subject.replace('"', '\\"')
        safe_body = body.replace('"', '\\"')
        applescript(f'''
        tell application "Mail"
            set newEmail to make new outgoing message with properties {{subject:"{safe_subj}", content:"{safe_body}"}}
            tell newEmail
                make new to recipient at end of to recipients with properties {{address:"{safe_to}"}}
                send
            end tell
        end tell
        ''')
        return f"Email sent to {to}, sir."
    return "Only available on macOS."

def play_music(song=None):
    if song:
        webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
        return f"Playing {song} on YouTube, sir."
    else:
        if IS_MAC:
            open_app("Music")
            return "Opening Music app, sir."
        webbrowser.open("https://www.youtube.com/results?search_query=music")
        return "Playing music, sir."

def list_running_apps():
    if IS_MAC:
        result = applescript('tell application "System Events" to get name of every process whose background only is false')
        return f"Running apps: {result}"
    return "Only available on macOS."

def system_info():
    info = {"OS": platform.system() + " " + platform.release(), "Machine": platform.machine(), "Python": platform.python_version()}
    if IS_MAC:
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            info["CPU"] = cpu
            mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            info["RAM"] = f"{int(mem) // (1024**3)} GB"
            disk = subprocess.check_output(["df", "-h", "/"], text=True).split("\n")[1].split()
            info["Disk"] = f"{disk[2]} used / {disk[1]} total"
            battery = subprocess.check_output(["pmset", "-g", "batt"], text=True)
            if "Battery" in battery:
                info["Battery"] = battery.split("\n")[1].strip()
        except:
            pass
    return json.dumps(info, indent=2)

def create_file_desktop(filename, content=""):
    path = os.path.expanduser(f"~/Desktop/{filename}")
    with open(path, 'w') as f:
        f.write(content)
    return f"Created {filename} on your Desktop, sir."

def empty_trash():
    if IS_MAC:
        applescript('tell application "Finder" to empty trash')
        return "Emptying trash, sir."
    return "Only available on macOS."

def lock_screen():
    if IS_MAC:
        subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
        return "Locking screen, sir."
    return "Only available on macOS."

def sleep_mac():
    if IS_MAC:
        subprocess.run(["pmset", "sleepnow"], capture_output=True)
        return "Goodnight, sir. Going to sleep."
    return "Only available on macOS."

def restart_mac():
    if IS_MAC:
        subprocess.Popen(["osascript", "-e", 'tell application "System Events" to restart'])
        return "Restarting your Mac, sir."
    return "Only available on macOS."

def shutdown_mac():
    if IS_MAC:
        subprocess.Popen(["osascript", "-e", 'tell application "System Events" to shut down'])
        return "Shutting down, sir."
    return "Only available on macOS."

# ===== API SKILLS =====

def get_weather(city="Lahore"):
    try:
        geocode = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1", timeout=10).json()
        if geocode.get("results"):
            lat = geocode["results"][0]["latitude"]
            lon = geocode["results"][0]["longitude"]
            weather = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m", timeout=10).json()
            c = weather.get("current", {})
            conditions = {0:"clear sky",1:"mainly clear",2:"partly cloudy",3:"overcast",45:"foggy",51:"light drizzle",53:"drizzle",55:"heavy drizzle",61:"light rain",63:"rain",65:"heavy rain",71:"light snow",73:"snow",75:"heavy snow",80:"rain showers",95:"thunderstorm"}
            return f"Weather in {city}: {c.get('temperature_2m',0)}C, {conditions.get(c.get('weather_code',0),'unknown')}, humidity {c.get('relative_humidity_2m',0)}%, wind {c.get('wind_speed_10m',0)} km/h"
        return f"Could not find city: {city}"
    except:
        return "Weather service unavailable, sir."

def get_news():
    try:
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:5]
        news = []
        for sid in story_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if story:
                news.append(f"{story.get('title', 'Unknown')}")
        return "Top tech news: " + ". ".join(news)
    except:
        return "News service unavailable, sir."

def get_joke():
    try:
        resp = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        data = resp.json()
        return f"{data['setup']} ... {data['punchline']}"
    except:
        return "Why don't programmers like nature? It has too many bugs."

def get_quote():
    try:
        resp = requests.get("https://api.quotable.io/random", timeout=5)
        data = resp.json()
        return f"{data['content']} — {data['author']}"
    except:
        return "The only way to do great work is to love what you do. — Steve Jobs"

def search_wikipedia(query):
    try:
        # Search API first to find the right article
        search_resp = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srprop=none&limit=1", timeout=10)
        results = search_resp.json().get("query", {}).get("search", [])
        if results:
            title = results[0]["title"]
            summary_resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}", timeout=10)
            if summary_resp.status_code == 200:
                return summary_resp.json().get("extract", "No info found, sir.")
        return f"No Wikipedia article found for {query}, sir."
    except:
        return "Wikipedia search unavailable, sir."

def get_ip_info():
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=10)
        data = resp.json()
        return f"Your IP: {data.get('ip')} | Location: {data.get('city')}, {data.get('country_name')} | ISP: {data.get('org')}"
    except:
        return "Could not fetch IP information, sir."

def get_crypto_price(coin="bitcoin"):
    try:
        resp = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd", timeout=10)
        data = resp.json()
        price = data.get(coin, {}).get("usd", 0)
        return f"{coin.capitalize()} is at ${price:,.2f} USD, sir."
    except:
        return "Crypto price service unavailable, sir."

def get_time_in_timezone(tz_name):
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
        now = datetime.datetime.now(tz)
        return f"It's {now.strftime('%I:%M %p')} in {tz_name}, sir."
    except:
        return f"Could not get time for {tz_name}, sir."

def get_word_definition(word):
    try:
        resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            definition = data[0]["meanings"][0]["definitions"][0]["definition"]
            return f"{word}: {definition}"
        return f"No definition found for {word}, sir."
    except:
        return "Dictionary service unavailable, sir."

def get_trivia():
    try:
        resp = requests.get("https://opentdb.com/api.php?amount=1&type=multiple", timeout=10)
        data = resp.json()
        q = data["results"][0]
        return f"Trivia: {q['question']} | Answer: {q['correct_answer']}"
    except:
        return "Trivia service unavailable, sir."

# ===== MAIN COMMAND PROCESSOR =====

def process_command(command):
    cmd = command.lower().strip()
    response = {"action": "speak", "text": "", "data": None}

    # Greetings
    if any(w in cmd for w in ["hello jarvis", "hi jarvis", "hey jarvis", "jarvis are you there", "jarvis you there", "good morning", "good evening"]):
        response["text"] = "Yes sir, JARVIS is here. How may I assist you?"
    elif "how are you" in cmd:
        response["text"] = "All systems operational, sir. Ready to assist."

    # Time
    elif "time" in cmd and ("what" in cmd or "tell" in cmd or cmd == "time"):
        response["text"] = f"It's {datetime.datetime.now().strftime('%I:%M %p')}, sir."

    # Date
    elif "date" in cmd or ("today" in cmd and "what" in cmd):
        response["text"] = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, sir."

    # Weather
    elif "weather" in cmd:
        city = "Lahore"
        if "in" in cmd.split():
            idx = cmd.split().index("in")
            if idx + 1 < len(cmd.split()):
                city = " ".join(cmd.split()[idx+1:])
        response["text"] = get_weather(city)

    # News
    elif "news" in cmd:
        response["text"] = get_news()

    # Open VS Code
    elif "vs code" in cmd or "vscode" in cmd or "visual studio" in cmd:
        if "open" in cmd or "launch" in cmd or "start" in cmd:
            path_match = [w for w in cmd.split() if "/" in w or w.endswith(".py") or w.endswith(".js")]
            response["text"] = open_vscode(path_match[0] if path_match else None)

    # Open GitHub Desktop
    elif "github" in cmd and ("desktop" in cmd or "open" in cmd or "launch" in cmd):
        response["text"] = open_github_desktop()

    # Git operations
    elif "git clone" in cmd:
        url = cmd.replace("git clone ", "").replace("clone ", "").strip()
        response["text"] = git_clone(url)

    elif "git push" in cmd or "commit and push" in cmd or "push to github" in cmd:
        msg = "Update"
        if "message" in cmd:
            idx = cmd.split().index("message")
            if idx + 1 < len(cmd.split()):
                msg = " ".join(cmd.split()[idx+1:])
        response["text"] = git_commit_push(msg)

    # Open Terminal
    elif "open terminal" in cmd or "launch terminal" in cmd:
        response["text"] = open_terminal()

    # Run terminal command
    elif cmd.startswith("run ") or cmd.startswith("execute "):
        terminal_cmd = cmd.replace("run ", "").replace("execute ", "")
        response["text"] = run_terminal_command(terminal_cmd)

    # Create project
    elif cmd.startswith("create project") or cmd.startswith("new project"):
        words = cmd.replace("create project ", "").replace("new project ", "").split()
        name = words[0] if words else "new_project"
        ptype = "python"
        if "web" in cmd or "html" in cmd:
            ptype = "web"
        response["text"] = create_project(name, ptype)
        if IS_MAC:
            time.sleep(1)
            open_vscode(os.path.expanduser(f"~/Desktop/{name}"))

    # Open website or Mac app
    elif cmd.startswith("open ") or cmd.startswith("go to "):
        site = cmd.replace("open ", "").replace("go to ", "")
        MAC_APPS = ["safari","notes","mail","music","messages","facetime","calendar","reminders",
                     "maps","photos","preview","calculator","terminal","finder","settings",
                     "system settings","app store","contacts","textedit","stickies","activity monitor"]
        if site.lower() in MAC_APPS:
            response["text"] = open_app(site.title())
        else:
            site_map = {
                "youtube": "youtube.com", "google": "google.com", "facebook": "facebook.com",
                "twitter": "twitter.com", "github": "github.com", "gmail": "gmail.com",
                "whatsapp": "web.whatsapp.com", "instagram": "instagram.com",
                "linkedin": "linkedin.com", "spotify": "open.spotify.com",
                "netflix": "netflix.com", "amazon": "amazon.com", "chatgpt": "chat.openai.com",
                "base44": "app.base44.com", "reddit": "reddit.com", "wikipedia": "wikipedia.org"
            }
            if "." in site or site.lower() in site_map:
                site = site_map.get(site, site if "." in site else site + ".com")
                if not site.startswith("http"):
                    site = "https://" + site
                webbrowser.open(site)
                response["text"] = f"Opening {site}, sir."
            else:
                response["text"] = open_app(site.title())

    # Open Mac app
    elif cmd.startswith("launch ") or cmd.startswith("open app") or cmd.startswith("start "):
        app_name = cmd.replace("launch ", "").replace("open app ", "").replace("start ", "")
        if "." not in app_name and "http" not in app_name:
            response["text"] = open_app(app_name.title())
        else:
            webbrowser.open(app_name)
            response["text"] = f"Opening {app_name}, sir."

    # Close app
    elif cmd.startswith("close ") or cmd.startswith("quit "):
        app_name = cmd.replace("close ", "").replace("quit ", "")
        response["text"] = close_app(app_name.title())

    # Running apps
    elif "running" in cmd and ("app" in cmd or "application" in cmd):
        response["text"] = list_running_apps()

    # Type text
    elif cmd.startswith("type "):
        text = cmd.replace("type ", "")
        response["text"] = type_in_app(text)

    # Press key
    elif cmd.startswith("press "):
        key = cmd.replace("press ", "")
        response["text"] = press_key(key)

    # Copy paste
    elif "copy paste" in cmd or (cmd == "paste"):
        response["text"] = copy_paste()

    # Volume
    elif "volume" in cmd:
        for word in cmd.split():
            if word.isdigit():
                response["text"] = set_volume(word)
                break
        else:
            if "up" in cmd:
                applescript("set volume output volume (output volume of (get volume settings)) + 10") if IS_MAC else None
                response["text"] = "Volume up, sir."
            elif "down" in cmd:
                applescript("set volume output volume (output volume of (get volume settings)) - 10") if IS_MAC else None
                response["text"] = "Volume down, sir."
            elif "mute" in cmd:
                set_volume(0) if IS_MAC else None
                response["text"] = "Muted, sir."
            else:
                response["text"] = get_volume()

    # Screenshot
    elif "screenshot" in cmd:
        response["text"] = take_screenshot()

    # Create file
    elif cmd.startswith("create file") or cmd.startswith("new file"):
        filename = cmd.replace("create file ", "").replace("new file ", "")
        if not filename:
            filename = f"untitled_{int(time.time())}.txt"
        response["text"] = create_file_desktop(filename)

    # Create note
    elif cmd.startswith("note ") or cmd.startswith("create note"):
        content = cmd.replace("note ", "").replace("create note ", "")
        response["text"] = create_note("JARVIS Note", content)

    # Create reminder
    elif cmd.startswith("remind ") or cmd.startswith("reminder "):
        text = cmd.replace("remind ", "").replace("reminder ", "")
        response["text"] = create_reminder(text)

    # Send iMessage
    elif cmd.startswith("send message") or cmd.startswith("message "):
        response["text"] = "To send a message, say: send message to [phone] saying [message], sir."

    # Send email
    elif cmd.startswith("send email") or cmd.startswith("email "):
        response["text"] = "To send email, say: send email to [address] subject [subject] body [message], sir."

    # Open folder
    elif cmd.startswith("open ") and any(f in cmd for f in ["desktop", "documents", "downloads", "pictures", "music", "movies", "applications", "home folder"]):
        folder = cmd.replace("open ", "").replace(" folder", "")
        response["text"] = open_folder(folder)

    # Empty trash
    elif "empty trash" in cmd or "clear trash" in cmd:
        response["text"] = empty_trash()

    # Lock screen
    elif "lock" in cmd and "screen" in cmd or cmd == "lock":
        response["text"] = lock_screen()

    # Sleep
    elif "sleep" in cmd and "mac" in cmd or cmd == "sleep":
        response["text"] = sleep_mac()

    # Restart
    elif "restart" in cmd:
        response["text"] = restart_mac()

    # Shutdown
    elif "shutdown" in cmd and "jarvis" not in cmd:
        response["text"] = shutdown_mac()

    # Wikipedia
    elif "what is" in cmd or "who is" in cmd or "tell me about" in cmd or "search wikipedia" in cmd:
        query = cmd.replace("what is ", "").replace("who is ", "").replace("tell me about ", "").replace("search wikipedia for ", "").replace("search wikipedia ", "")
        response["text"] = search_wikipedia(query)

    # Joke
    elif "joke" in cmd:
        response["text"] = get_joke()

    # Quote
    elif "quote" in cmd:
        response["text"] = get_quote()

    # Trivia
    elif "trivia" in cmd:
        response["text"] = get_trivia()

    # Dictionary
    elif "define" in cmd or "definition" in cmd:
        word = cmd.replace("define ", "").replace("definition of ", "").replace("definition ", "")
        response["text"] = get_word_definition(word)

    # Crypto
    elif "bitcoin" in cmd or "ethereum" in cmd or "crypto" in cmd or "doge" in cmd:
        coin = "bitcoin"
        if "ethereum" in cmd or "ether" in cmd: coin = "ethereum"
        elif "doge" in cmd: coin = "dogecoin"
        response["text"] = get_crypto_price(coin)

    # System info
    elif "system" in cmd and ("info" in cmd or "status" in cmd):
        response["text"] = "Retrieving system information, sir."
        response["data"] = {"type": "system", "info": system_info()}

    # IP
    elif "ip address" in cmd or "my ip" in cmd:
        response["text"] = get_ip_info()

    # Time in timezone
    elif "time in" in cmd:
        tz = cmd.replace("time in ", "").replace("what time is it in ", "").strip()
        tz_map = {"london":"Europe/London","new york":"America/New_York","tokyo":"Asia/Tokyo","dubai":"Asia/Dubai","karachi":"Asia/Karachi","lahore":"Asia/Karachi","paris":"Europe/Paris","sydney":"Australia/Sydney","singapore":"Asia/Singapore","los angeles":"America/Los_Angeles","toronto":"America/Toronto"}
        response["text"] = get_time_in_timezone(tz_map.get(tz, tz))

    # Play music
    elif "play" in cmd and ("music" in cmd or "song" in cmd):
        song = cmd.replace("play ", "").replace("music", "").replace("song", "").strip()
        response["text"] = play_music(song if song else None)

    # Calculate
    elif "calculate" in cmd or any(op in cmd for op in ["plus","minus","times","divided"]):
        expr = cmd.replace("calculate ","").replace("what is ","").replace("what's ","")
        expr = expr.replace("plus","+").replace("minus","-").replace("times","*").replace("divided by","/").replace("x","*")
        if all(c in "0123456789+-*/.() " for c in expr):
            try:
                response["text"] = f"The answer is {eval(expr)}, sir."
            except:
                response["text"] = "I couldn't calculate that, sir."
        else:
            response["text"] = "I can only do basic math, sir."

    # Clear
    elif "clear" in cmd or "reset" in cmd:
        response["text"] = "Interface cleared, sir."
        response["data"] = {"type": "clear"}

    # Help
    elif "help" in cmd or "what can you do" in cmd:
        response["text"] = "I have 50+ skills, sir. Check the panel on the left side of the screen."

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
        response["text"] = f"I searched the web for {command}, sir. Check your browser."

    # SPEAK the response using macOS native voice
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
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #000; color: #00aaff; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; height: 100vh; display: flex; flex-direction: column; align-items: center; }
.header { position: fixed; top: 0; width: 100%; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; z-index: 100; }
.logo { font-size: 14px; letter-spacing: 4px; color: #00aaff; opacity: 0.7; }
.status { font-size: 11px; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.status-listening .status-dot { background: #ffc800; animation: pulse 1s infinite; }
.status-thinking .status-dot { background: #9966ff; animation: pulse 0.5s infinite; }
.status-idle .status-dot { background: #00ff88; animation: pulse 2s infinite; }
.status-speaking .status-dot { background: #00aaff; animation: pulse 0.8s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
.reactor { position: relative; width: 300px; height: 300px; margin-top: 40px; display: flex; align-items: center; justify-content: center; }
.reactor-ring { position: absolute; border-radius: 50%; }
.r1 { width: 300px; height: 300px; border: 1px solid rgba(0,170,255,0.2); animation: spin 10s linear infinite; }
.r2 { width: 240px; height: 240px; border: 2px solid rgba(0,170,255,0.3); animation: spin 7s linear infinite reverse; }
.r3 { width: 180px; height: 180px; border: 1px solid rgba(0,170,255,0.4); animation: spin 5s linear infinite; }
.r4 { width: 120px; height: 120px; border: 2px solid rgba(0,170,255,0.5); animation: spin 3s linear infinite reverse; }
.r-core { width: 70px; height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0,170,255,0.8), rgba(0,100,200,0.3), transparent); box-shadow: 0 0 50px rgba(0,170,255,0.6); animation: corepulse 2s ease-in-out infinite; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #fff; letter-spacing: 1px; }
@keyframes corepulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.1); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.reactor-listening .r-core { background: radial-gradient(circle, rgba(255,200,0,0.8), rgba(255,100,0,0.3), transparent); box-shadow: 0 0 70px rgba(255,200,0,0.6); }
.reactor-thinking .r-core { background: radial-gradient(circle, rgba(150,100,255,0.8), rgba(100,100,200,0.3), transparent); box-shadow: 0 0 70px rgba(150,100,255,0.6); }
.reactor-speaking .r-core { background: radial-gradient(circle, rgba(0,170,255,0.9), rgba(0,100,200,0.4), transparent); box-shadow: 0 0 80px rgba(0,170,255,0.8); }
.auto-mode { position: fixed; top: 50px; right: 20px; display: flex; align-items: center; gap: 8px; z-index: 100; }
.auto-toggle { width: 44px; height: 24px; border-radius: 12px; background: rgba(0,170,255,0.2); border: 1px solid rgba(0,170,255,0.4); cursor: pointer; position: relative; }
.auto-toggle.on { background: rgba(0,255,136,0.3); border-color: #00ff88; }
.auto-toggle .knob { width: 18px; height: 18px; border-radius: 50%; background: #00aaff; position: absolute; top: 2px; left: 2px; transition: all 0.3s; }
.auto-toggle.on .knob { left: 22px; background: #00ff88; }
.auto-label { font-size: 11px; color: rgba(0,170,255,0.6); }
.voice-mode { position: fixed; top: 50px; right: 140px; display: flex; align-items: center; gap: 8px; z-index: 100; }
.voice-toggle { width: 44px; height: 24px; border-radius: 12px; background: rgba(0,170,255,0.2); border: 1px solid rgba(0,170,255,0.4); cursor: pointer; position: relative; }
.voice-toggle.on { background: rgba(0,170,255,0.3); border-color: #00aaff; }
.voice-toggle .knob { width: 18px; height: 18px; border-radius: 50%; background: #666; position: absolute; top: 2px; left: 2px; transition: all 0.3s; }
.voice-toggle.on .knob { left: 22px; background: #00aaff; }
.voice-label { font-size: 11px; color: rgba(0,170,255,0.6); }
.skills-panel { position: fixed; top: 45px; left: 8px; width: 195px; max-height: 85vh; overflow-y: auto; padding: 5px; }
.skills-title { font-size: 10px; color: rgba(0,170,255,0.4); letter-spacing: 2px; margin-bottom: 6px; padding-left: 4px; }
.skill-cat { font-size: 9px; color: rgba(0,255,136,0.4); margin: 8px 0 4px 4px; letter-spacing: 1px; }
.skill-btn { padding: 5px 10px; margin-bottom: 3px; border-radius: 14px; background: rgba(0,170,255,0.05); border: 1px solid rgba(0,170,255,0.15); color: rgba(0,170,255,0.5); font-size: 10px; cursor: pointer; transition: all 0.15s; }
.skill-btn:hover { background: rgba(0,170,255,0.15); border-color: rgba(0,170,255,0.4); color: #00aaff; }
.conversation { position: fixed; top: 85px; right: 20px; width: 320px; max-height: 50vh; overflow-y: auto; padding: 5px; }
.msg { margin-bottom: 8px; padding: 8px 12px; border-radius: 12px; font-size: 12px; line-height: 1.5; opacity: 0; animation: fadeIn 0.3s forwards; }
@keyframes fadeIn { to { opacity: 1; } }
.msg.user { background: rgba(0,170,255,0.1); border: 1px solid rgba(0,170,255,0.2); text-align: right; margin-left: 40px; }
.msg.jarvis { background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.2); margin-right: 40px; }
.msg .label { font-size: 9px; color: rgba(255,255,255,0.3); margin-bottom: 2px; }
.status-text { position: fixed; top: 50%; left: 50%; transform: translate(-50%, 80px); font-size: 12px; color: rgba(0,170,255,0.6); letter-spacing: 2px; text-align: center; width: 300px; }
.controls { position: fixed; bottom: 0; width: 100%; padding: 15px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.mic-btn { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #00aaff; background: rgba(0,170,255,0.1); color: #00aaff; cursor: pointer; font-size: 20px; display: flex; align-items: center; justify-content: center; transition: all 0.3s; }
.mic-btn:hover { background: rgba(0,170,255,0.3); box-shadow: 0 0 20px rgba(0,170,255,0.5); }
.mic-btn.listening { background: rgba(255,200,0,0.3); border-color: #ffc800; box-shadow: 0 0 30px rgba(255,200,0,0.6); animation: pulse 1s infinite; }
.mic-btn.auto { background: rgba(0,255,136,0.2); border-color: #00ff88; }
.command-bar { position: relative; width: 80%; max-width: 600px; }
.command-input { width: 100%; padding: 10px 40px 10px 18px; border-radius: 25px; background: rgba(0,170,255,0.05); border: 1px solid rgba(0,170,255,0.3); color: #00aaff; font-size: 13px; outline: none; font-family: 'Helvetica Neue', Arial; }
.command-input:focus { border-color: rgba(0,170,255,0.6); box-shadow: 0 0 15px rgba(0,170,255,0.2); }
.command-input::placeholder { color: rgba(0,170,255,0.3); }
.send-btn { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #00aaff; cursor: pointer; font-size: 16px; }
.data-display { position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 500px; max-height: 120px; overflow-y: auto; display: none; }
.data-display.active { display: block; }
.data-card { background: rgba(0,170,255,0.05); border: 1px solid rgba(0,170,255,0.2); border-radius: 8px; padding: 12px; margin-top: 4px; font-size: 11px; }
.data-card h4 { color: #00aaff; margin-bottom: 6px; font-size: 12px; }
.data-card pre { color: rgba(0,255,136,0.7); white-space: pre-wrap; font-size: 10px; }
.mic-prompt { position: fixed; top: 45%; left: 50%; transform: translateX(-50%); background: rgba(255,200,0,0.1); border: 1px solid rgba(255,200,0,0.3); border-radius: 10px; padding: 10px 20px; font-size: 12px; color: rgba(255,200,0,0.7); z-index: 200; display: none; }
.mic-prompt.show { display: block; animation: fadeIn 0.3s forwards; }
</style>
</head>
<body>

<div class="header">
    <div class="logo">J.A.R.V.I.S v3.0</div>
    <div class="status status-idle" id="statusBar"><span class="status-dot"></span><span id="statusText">ONLINE</span></div>
</div>

<div class="voice-mode">
    <span class="voice-label">VOICE</span>
    <div class="voice-toggle on" id="voiceToggle" onclick="toggleVoiceOutput()"><div class="knob"></div></div>
</div>

<div class="auto-mode">
    <span class="auto-label">AUTO-LISTEN</span>
    <div class="auto-toggle on" id="autoToggle" onclick="toggleAutoListen()"><div class="knob"></div></div>
</div>

<div class="skills-panel">
    <div class="skills-title">SKILLS (50+)</div>
    <div class="skill-cat">DAILY</div>
    <div class="skill-btn" onclick="sendCmd('what time is it')">Time</div>
    <div class="skill-btn" onclick="sendCmd('what is the date')">Date</div>
    <div class="skill-btn" onclick="sendCmd('weather in Lahore')">Weather</div>
    <div class="skill-btn" onclick="sendCmd('news')">News</div>
    <div class="skill-cat">DESKTOP CONTROL</div>
    <div class="skill-btn" onclick="sendCmd('open safari')">Safari</div>
    <div class="skill-btn" onclick="sendCmd('open notes')">Notes</div>
    <div class="skill-btn" onclick="sendCmd('open music')">Music</div>
    <div class="skill-btn" onclick="sendCmd('open mail')">Mail</div>
    <div class="skill-btn" onclick="sendCmd('open finder')">Finder</div>
    <div class="skill-btn" onclick="sendCmd('open calculator')">Calculator</div>
    <div class="skill-btn" onclick="sendCmd('open terminal')">Terminal</div>
    <div class="skill-btn" onclick="sendCmd('open system settings')">Settings</div>
    <div class="skill-btn" onclick="sendCmd('close safari')">Close App</div>
    <div class="skill-btn" onclick="sendCmd('running apps')">Running Apps</div>
    <div class="skill-cat">VS CODE & GIT</div>
    <div class="skill-btn" onclick="sendCmd('open vs code')">VS Code</div>
    <div class="skill-btn" onclick="sendCmd('open github desktop')">GitHub Desktop</div>
    <div class="skill-btn" onclick="sendCmd('create project myapp python')">New Project</div>
    <div class="skill-btn" onclick="sendCmd('commit and push')">Git Push</div>
    <div class="skill-cat">MAC SYSTEM</div>
    <div class="skill-btn" onclick="sendCmd('volume up')">Volume Up</div>
    <div class="skill-btn" onclick="sendCmd('volume down')">Volume Down</div>
    <div class="skill-btn" onclick="sendCmd('screenshot')">Screenshot</div>
    <div class="skill-btn" onclick="sendCmd('system info')">System Info</div>
    <div class="skill-btn" onclick="sendCmd('lock screen')">Lock Mac</div>
    <div class="skill-btn" onclick="sendCmd('sleep')">Sleep Mac</div>
    <div class="skill-btn" onclick="sendCmd('empty trash')">Empty Trash</div>
    <div class="skill-cat">FOLDERS</div>
    <div class="skill-btn" onclick="sendCmd('open desktop')">Desktop</div>
    <div class="skill-btn" onclick="sendCmd('open documents')">Documents</div>
    <div class="skill-btn" onclick="sendCmd('open downloads')">Downloads</div>
    <div class="skill-cat">PRODUCTIVITY</div>
    <div class="skill-btn" onclick="sendCmd('note buy groceries')">Note</div>
    <div class="skill-btn" onclick="sendCmd('remind call mom')">Reminder</div>
    <div class="skill-cat">KNOWLEDGE</div>
    <div class="skill-btn" onclick="sendCmd('what is artificial intelligence')">Wikipedia</div>
    <div class="skill-btn" onclick="sendCmd('define computer')">Dictionary</div>
    <div class="skill-btn" onclick="sendCmd('joke')">Joke</div>
    <div class="skill-btn" onclick="sendCmd('quote')">Quote</div>
    <div class="skill-cat">FINANCE</div>
    <div class="skill-btn" onclick="sendCmd('bitcoin price')">Bitcoin</div>
    <div class="skill-cat">WEB</div>
    <div class="skill-btn" onclick="sendCmd('open youtube')">YouTube</div>
    <div class="skill-btn" onclick="sendCmd('open google')">Google</div>
    <div class="skill-btn" onclick="sendCmd('play music')">Play Music</div>
    <div class="skill-btn" onclick="sendCmd('my ip address')">IP Address</div>
    <div class="skill-btn" onclick="sendCmd('time in london')">Time in London</div>
    <div class="skill-btn" onclick="sendCmd('time in new york')">Time in NY</div>
</div>

<div class="reactor" id="reactor">
    <div class="reactor-ring r1"></div>
    <div class="reactor-ring r2"></div>
    <div class="reactor-ring r3"></div>
    <div class="reactor-ring r4"></div>
    <div class="r-core" id="core">JARVIS</div>
</div>

<div class="status-text" id="bootText">Say "JARVIS" then your command, sir</div>
<div class="mic-prompt" id="micPrompt">Microphone access needed. Please allow in browser settings.</div>

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
let recognition = null;
let isListening = false;
let autoListen = true;
let voiceOutput = true;
let wakeWordDetected = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (e) => {
        let fullTranscript = '';
        let isFinal = false;
        for (let i = e.resultIndex; i < e.results.length; i++) {
            fullTranscript += e.results[i][0].transcript;
            if (e.results[i].isFinal) isFinal = true;
        }
        fullTranscript = fullTranscript.toLowerCase().trim();

        if (autoListen) {
            if (fullTranscript.includes('jarvis') || fullTranscript.includes('travis') || fullTranscript.includes('jeff')) {
                wakeWordDetected = true;
                setReactorState('listening');
                let command = fullTranscript.replace(/.*jarvis[, ]*/,'').replace(/.*travis[, ]*/,'').replace(/.*jeff[, ]*/,'').trim();
                if (command && isFinal) {
                    addMessage('user', command);
                    sendToJarvis(command);
                    wakeWordDetected = false;
                } else if (command) {
                    document.getElementById('commandInput').value = command;
                }
            } else if (wakeWordDetected && fullTranscript) {
                document.getElementById('commandInput').value = fullTranscript;
                if (isFinal) {
                    addMessage('user', fullTranscript);
                    sendToJarvis(fullTranscript);
                    wakeWordDetected = false;
                }
            }
        } else {
            document.getElementById('commandInput').value = fullTranscript;
            if (isFinal && fullTranscript) {
                sendInput();
            }
        }
    };

    recognition.onerror = (e) => {
        console.log('Speech error:', e.error);
        if (e.error === 'not-allowed') {
            document.getElementById('micPrompt').classList.add('show');
            setTimeout(() => document.getElementById('micPrompt').classList.remove('show'), 5000);
        }
        if (autoListen && e.error !== 'not-allowed') {
            setTimeout(startAutoListening, 1000);
        }
    };

    recognition.onend = () => {
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        if (autoListen) {
            setTimeout(startAutoListening, 500);
        } else {
            setReactorState('idle');
        }
    };
}

function startAutoListening() {
    if (!recognition || isListening) return;
    try {
        recognition.start();
        isListening = true;
        document.getElementById('micBtn').classList.add('listening');
        setReactorState('idle');
    } catch(e) {}
}

function toggleAutoListen() {
    autoListen = !autoListen;
    const toggle = document.getElementById('autoToggle');
    if (autoListen) {
        toggle.classList.add('on');
        startAutoListening();
    } else {
        toggle.classList.remove('on');
        if (isListening) recognition.stop();
    }
}

function toggleVoiceOutput() {
    voiceOutput = !voiceOutput;
    document.getElementById('voiceToggle').classList.toggle('on', voiceOutput);
}

function toggleVoice() {
    if (!recognition) {
        addMessage('jarvis', 'Voice recognition requires Safari or Chrome, sir.');
        return;
    }
    autoListen = false;
    document.getElementById('autoToggle').classList.remove('on');
    if (isListening) {
        recognition.stop();
    } else {
        try { recognition.start(); isListening = true; document.getElementById('micBtn').classList.add('listening'); setReactorState('listening'); } catch(e) {}
    }
}

function setReactorState(state) {
    const reactor = document.getElementById('reactor');
    const core = document.getElementById('core');
    const boot = document.getElementById('bootText');
    const sb = document.getElementById('statusBar');
    reactor.classList.remove('reactor-listening','reactor-thinking','reactor-speaking');
    sb.classList.remove('status-idle','status-listening','status-thinking','status-speaking');
    if (state === 'listening') { reactor.classList.add('reactor-listening'); sb.classList.add('status-listening'); core.textContent='LISTEN'; boot.textContent='I am listening, sir...'; document.getElementById('statusText').textContent='LISTENING'; }
    else if (state === 'thinking') { reactor.classList.add('reactor-thinking'); sb.classList.add('status-thinking'); core.textContent='PROC'; boot.textContent='Processing, sir...'; document.getElementById('statusText').textContent='PROCESSING'; }
    else if (state === 'speaking') { reactor.classList.add('reactor-speaking'); sb.classList.add('status-speaking'); core.textContent='SPEAK'; boot.textContent='Speaking, sir...'; document.getElementById('statusText').textContent='SPEAKING'; }
    else { sb.classList.add('status-idle'); core.textContent='JARVIS'; boot.textContent='Say "JARVIS" then your command, sir'; document.getElementById('statusText').textContent=autoListen?'AUTO-LISTEN':'ONLINE'; }
}

function sendCmd(cmd) { addMessage('user', cmd); sendToJarvis(cmd); }
function sendInput() { const i=document.getElementById('commandInput'); const c=i.value.trim(); if(!c) return; i.value=''; addMessage('user', c); sendToJarvis(c); }

function sendToJarvis(command) {
    setReactorState('thinking');
    fetch('/api/command', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({command:command}) })
    .then(r => r.json())
    .then(data => {
        setReactorState('speaking');
        addMessage('jarvis', data.text);
        if (data.data) displayData(data.data);
        // JARVIS speaks via macOS 'say' command on the backend
        // Also speak via browser as backup
        if (voiceOutput && 'speechSynthesis' in window) {
            speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(data.text);
            u.rate = 0.95; u.pitch = 0.85; u.volume = 0.8;
            const voices = speechSynthesis.getVoices();
            const pref = voices.find(v => v.name.includes('Daniel') || v.name.includes('Arthur'));
            if (pref) u.voice = pref;
            u.onend = () => setReactorState('idle');
            speechSynthesis.speak(u);
        } else {
            setTimeout(() => setReactorState('idle'), 2000);
        }
    })
    .catch(e => { setReactorState('idle'); addMessage('jarvis', 'Connection error, sir.'); });
}

function addMessage(sender, text) {
    const c = document.getElementById('conversation');
    const m = document.createElement('div');
    m.className = 'msg ' + sender;
    m.innerHTML = '<div class="label">'+(sender==='user'?'YOU':'JARVIS')+'</div>'+text;
    c.appendChild(m); c.scrollTop = c.scrollHeight;
}

function displayData(data) {
    const d = document.getElementById('dataDisplay');
    if (data.type === 'system') { d.innerHTML = '<div class="data-card"><h4>SYSTEM INFO</h4><pre>'+data.info+'</pre></div>'; d.classList.add('active'); }
    else if (data.type === 'clear') { document.getElementById('conversation').innerHTML=''; d.classList.remove('active'); }
    else if (data.type === 'shutdown_jarvis') { setTimeout(()=>window.close(), 3000); }
}

// Boot
setTimeout(() => {
    addMessage('jarvis', 'JARVIS v3.0 online, sir. Voice is active. Auto-listening is ON. Just say JARVIS followed by your command.');
    setTimeout(startAutoListening, 1500);
}, 800);

if ('speechSynthesis' in window) { speechSynthesis.onvoiceschanged = () => {}; speechSynthesis.getVoices(); }
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

@app.route('/api/voice_status')
def voice_status():
    return jsonify({"mac_voice": IS_MAC, "message": "Voice is active via macOS native 'say' command"})

if __name__ == '__main__':
    print("=" * 55)
    print("  J.A.R.V.I.S v3.0 — AI Assistant")
    print("  Voice: macOS native 'say' (Daniel voice)")
    print("  Auto-listening: ON")
    print("  Say 'JARVIS' then your command")
    print("  Browser: http://localhost:7654")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    webbrowser.open("http://localhost:7654")
    app.run(host='0.0.0.0', port=7654, debug=False)
