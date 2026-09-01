#!/usr/bin/env python3
"""
JARVIS v2.0 — Complete AI Assistant with Auto-Listening
- Wake word detection ("Jarvis")
- 40+ skills
- Mac automation (open apps, control, execute tasks)
- Voice + text commands
- No mic button needed — always listening
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

# ===== MAC AUTOMATION =====

def mac_applescript(script):
    """Run AppleScript on macOS to control apps and system"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

def open_app(app_name):
    if platform.system() == "Darwin":
        mac_applescript(f'tell application "{app_name}" to activate')
        return f"Opening {app_name}, sir."
    return f"App control only available on macOS."

def close_app(app_name):
    if platform.system() == "Darwin":
        mac_applescript(f'tell application "{app_name}" to quit')
        return f"Closing {app_name}, sir."
    return f"App control only available on macOS."

def type_in_app(text):
    """Type text in the currently active app"""
    if platform.system() == "Darwin":
        mac_applescript(f'tell application "System Events" to keystroke "{text}"')
        return f"Typed: {text}"
    return "Typing only available on macOS."

def press_key(key):
    """Press a keyboard key"""
    if platform.system() == "Darwin":
        key_map = {
            "enter": "return", "return": "return", "tab": "tab",
            "space": "space", "escape": "escape", "esc": "escape",
            "delete": "delete", "backspace": "delete",
            "command": "command", "cmd": "command",
            "shift": "shift", "control": "control", "ctrl": "control",
            "option": "option", "alt": "option"
        }
        mac_key = key_map.get(key.lower(), key.lower())
        mac_applescript(f'tell application "System Events" to keystroke "{mac_key}"')
        return f"Pressed {key}"
    return "Key control only available on macOS."

def copy_paste():
    """Copy and paste"""
    if platform.system() == "Darwin":
        mac_applescript('tell application "System Events" to keystroke "c" using command down')
        time.sleep(0.2)
        mac_applescript('tell application "System Events" to keystroke "v" using command down')
        return "Copy and paste done, sir."
    return "Copy/paste only available on macOS."

def new_file_desktop(filename):
    """Create a new file on Desktop"""
    path = os.path.expanduser(f"~/Desktop/{filename}")
    with open(path, 'w') as f:
        f.write("")
    return f"Created {filename} on your Desktop, sir."

def open_folder(folder_name):
    """Open a folder in Finder"""
    if platform.system() == "Darwin":
        paths = {
            "desktop": "~/Desktop",
            "documents": "~/Documents",
            "downloads": "~/Downloads",
            "pictures": "~/Pictures",
            "music": "~/Music",
            "movies": "~/Movies",
            "applications": "/Applications",
            "home": "~"
        }
        path = paths.get(folder_name.lower(), folder_name)
        subprocess.Popen(["open", os.path.expanduser(path)])
        return f"Opening {folder_name}, sir."
    return "Folder control only available on macOS."

def set_volume(level):
    if platform.system() == "Darwin":
        mac_applescript(f"set volume output volume {int(level)}")
        return f"Volume set to {level}%, sir."

def get_volume():
    if platform.system() == "Darwin":
        result = mac_applescript("output volume of (get volume settings)")
        return f"Current volume is {result}%, sir."
    return "Volume control only available on macOS."

def set_brightness(level):
    if platform.system() == "Darwin":
        # Use brightness command if available
        try:
            subprocess.run(["brightness", str(int(level)/100)], capture_output=True)
            return f"Brightness set to {level}%, sir."
        except:
            return "Install brightness: brew install brightness. Or use your keyboard keys, sir."
    return "Brightness control only available on macOS."

def mac_message(phone, message_text):
    """Send a message via Messages app on Mac"""
    if platform.system() == "Darwin":
        script = f'''
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant "{phone}" of targetService
            send "{message_text}" to targetBuddy
        end tell
        '''
        mac_applescript(script)
        return f"Message sent to {phone}, sir."
    return "Messaging only available on macOS."

def mac_email(to, subject, body):
    """Send email via Mail app on Mac"""
    if platform.system() == "Darwin":
        script = f'''
        tell application "Mail"
            set newEmail to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
            tell newEmail
                make new to recipient at end of to recipients with properties {{address:"{to}"}}
                send
            end tell
        end tell
        '''
        mac_applescript(script)
        return f"Email sent to {to}, sir."
    return "Email only available on macOS."

def mac_note(title, content):
    """Create a note in Notes app"""
    if platform.system() == "Darwin":
        script = f'''
        tell application "Notes"
            tell account "iCloud"
                make new note with properties {{name:"{title}", body:"{content}"}}
            end tell
        end tell
        '''
        mac_applescript(script)
        return f"Note '{title}' created, sir."
    return "Notes only available on macOS."

def mac_reminder(text):
    """Create a reminder"""
    if platform.system() == "Darwin":
        script = f'tell application "Reminders" to make new reminder with properties {{name:"{text}"}}'
        mac_applescript(script)
        return f"Reminder added: {text}"
    return "Reminders only available on macOS."

def mac_search_spotlight(query):
    """Search using Spotlight"""
    if platform.system() == "Darwin":
        subprocess.Popen(["open", "-a", "Spotlight"])
        time.sleep(0.5)
        mac_applescript(f'tell application "System Events" to keystroke "{query}"')
        return f"Searching Spotlight for {query}, sir."
    return "Spotlight only available on macOS."

# ===== API-BASED SKILLS =====

def get_weather(city="Lahore"):
    try:
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
            return f"Weather in {city}: {temp}C, {condition}, humidity {humidity}%, wind {wind} km/h"
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
                news.append(f"- {story.get('title', 'Unknown')} ({story.get('score', 0)} upvotes)")
        return "Top tech news: " + " | ".join(news)
    except:
        return "News service unavailable, sir."

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
            return data.get("extract", "No information found, sir.")
        # Try search API
        search_resp = requests.get(
            f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json",
            timeout=10
        )
        if search_resp.status_code == 200:
            results = search_resp.json().get("query", {}).get("search", [])
            if results:
                title = results[0]["title"]
                summary_resp = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}",
                    timeout=10
                )
                if summary_resp.status_code == 200:
                    return summary_resp.json().get("extract", "No info found.")
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

def get_quote():
    try:
        resp = requests.get("https://api.quotable.io/random", timeout=5)
        data = resp.json()
        return f"{data['content']} — {data['author']}"
    except:
        return "The only way to do great work is to love what you do. — Steve Jobs"

def translate_text(text, target_lang="en"):
    # Free translation via MyMemory API
    try:
        resp = requests.get(
            f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_lang}",
            timeout=10
        )
        data = resp.json()
        return data.get("responseData", {}).get("translatedText", "Translation failed, sir.")
    except:
        return "Translation service unavailable, sir."

def get_crypto_price(coin="bitcoin"):
    try:
        resp = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd", timeout=10)
        data = resp.json()
        price = data.get(coin, {}).get("usd", 0)
        return f"{coin.capitalize()} is currently at ${price:,.2f} USD, sir."
    except:
        return "Crypto price service unavailable, sir."

def get_stock_info(symbol):
    return f"Stock information for {symbol} requires an API key, sir. I can check crypto prices instead."

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

# ===== SYSTEM INFO =====

def system_info():
    info = {"OS": platform.system() + " " + platform.release(), "Machine": platform.machine(), "Python": platform.python_version()}
    if platform.system() == "Darwin":
        try:
            cpu = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            info["CPU"] = cpu
            mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            info["RAM"] = f"{int(mem) // (1024**3)} GB"
            # Disk space
            disk = subprocess.check_output(["df", "-h", "/"], text=True).split("\n")[1].split()
            info["Disk"] = f"{disk[2]} used / {disk[1]} total"
            # Battery
            battery = subprocess.check_output(["pmset", "-g", "batt"], text=True)
            if "Battery" in battery:
                info["Battery"] = battery.split("\n")[1].strip()
        except:
            pass
    return json.dumps(info, indent=2)

def take_screenshot():
    if platform.system() == "Darwin":
        subprocess.Popen(["screencapture", "-x", os.path.expanduser("~/Desktop/jarvis_screenshot.png")])
        return "Screenshot saved to Desktop, sir."
    return "Screenshots only available on macOS."

def list_running_apps():
    if platform.system() == "Darwin":
        result = mac_applescript('tell application "System Events" to get name of every process whose background only is false')
        return f"Running apps: {result}"
    return "Only available on macOS."

# ===== COMMAND PROCESSOR =====

def process_command(command):
    cmd = command.lower().strip()
    response = {"action": "speak", "text": "", "data": None}

    # Greetings
    if any(w in cmd for w in ["hello", "hi jarvis", "hey jarvis", "jarvis are you there", "jarvis you there"]):
        response["text"] = "Yes sir, JARVIS is here and ready to assist you."
    elif "how are you" in cmd:
        response["text"] = "All systems operational, sir. How may I assist you?"

    # Time
    elif "time" in cmd and ("what" in cmd or "tell" in cmd or cmd == "time"):
        now = datetime.datetime.now()
        response["text"] = f"It's {now.strftime('%I:%M %p')}, sir."

    # Date
    elif "date" in cmd or ("today" in cmd and "what" in cmd):
        response["text"] = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, sir."

    # Weather
    elif "weather" in cmd:
        city = "Lahore"
        words = cmd.split()
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = " ".join(words[idx+1:])
        response["text"] = get_weather(city)

    # News
    elif "news" in cmd:
        response["text"] = get_news()

    # Open website
    elif cmd.startswith("open ") or cmd.startswith("go to "):
        site = cmd.replace("open ", "").replace("go to ", "")
        site_map = {
            "youtube": "youtube.com", "google": "google.com", "facebook": "facebook.com",
            "twitter": "twitter.com", "x": "twitter.com", "github": "github.com",
            "gmail": "gmail.com", "whatsapp": "web.whatsapp.com", "instagram": "instagram.com",
            "linkedin": "linkedin.com", "maps": "maps.apple.com", "spotify": "open.spotify.com",
            "netflix": "netflix.com", "amazon": "amazon.com", "chatgpt": "chat.openai.com",
            "base44": "app.base44.com", "reddit": "reddit.com", "wikipedia": "wikipedia.org"
        }
        site = site_map.get(site, site if "." in site else site + ".com")
        if not site.startswith("http"):
            site = "https://" + site
        webbrowser.open(site)
        response["text"] = f"Opening {site}, sir."

    # Open Mac app
    elif cmd.startswith("launch ") or cmd.startswith("open app ") or cmd.startswith("start "):
        app_name = cmd.replace("launch ", "").replace("open app ", "").replace("start ", "")
        # Don't confuse with "open website"
        if "http" not in app_name and "." not in app_name:
            response["text"] = open_app(app_name.title())
        else:
            response["text"] = open_website(app_name)

    # Close app
    elif cmd.startswith("close ") or cmd.startswith("quit "):
        app_name = cmd.replace("close ", "").replace("quit ", "")
        response["text"] = close_app(app_name.title())

    # Running apps
    elif "running" in cmd and "app" in cmd:
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
    elif "copy paste" in cmd or "paste" in cmd:
        response["text"] = copy_paste()

    # Volume
    elif "volume" in cmd:
        for word in cmd.split():
            if word.isdigit():
                response["text"] = set_volume(word)
                break
        else:
            if "up" in cmd:
                mac_applescript("set volume output volume (output volume of (get volume settings)) + 10")
                response["text"] = "Volume up, sir."
            elif "down" in cmd:
                mac_applescript("set volume output volume (output volume of (get volume settings)) - 10")
                response["text"] = "Volume down, sir."
            elif "mute" in cmd:
                mac_applescript("set volume output volume 0")
                response["text"] = "Muted, sir."
            else:
                response["text"] = get_volume()

    # Brightness
    elif "brightness" in cmd:
        for word in cmd.split():
            if word.isdigit():
                response["text"] = set_brightness(word)
                break
        else:
            response["text"] = "Say brightness up, down, or brightness followed by a number."

    # Screenshot
    elif "screenshot" in cmd:
        response["text"] = take_screenshot()

    # Create file
    elif cmd.startswith("create file") or cmd.startswith("new file"):
        filename = cmd.replace("create file ", "").replace("new file ", "")
        if not filename:
            filename = f"untitled_{int(time.time())}.txt"
        response["text"] = new_file_desktop(filename)

    # Open folder
    elif cmd.startswith("open ") and any(f in cmd for f in ["desktop", "documents", "downloads", "pictures", "music", "movies", "applications", "home folder"]):
        folder = cmd.replace("open ", "").replace(" folder", "")
        response["text"] = open_folder(folder)

    # Spotlight search
    elif cmd.startswith("search ") and "for" in cmd:
        query = cmd.replace("search for ", "").replace("search ", "")
        response["text"] = mac_search_spotlight(query)

    # Send message (Mac Messages)
    elif cmd.startswith("send message") or cmd.startswith("message "):
        response["text"] = "To send a message, say: send message to [phone number] saying [message], sir."

    # Create note
    elif cmd.startswith("note ") or cmd.startswith("create note"):
        content = cmd.replace("note ", "").replace("create note ", "")
        response["text"] = mac_note("JARVIS Note", content)

    # Create reminder
    elif cmd.startswith("remind ") or cmd.startswith("reminder "):
        text = cmd.replace("remind ", "").replace("reminder ", "")
        response["text"] = mac_reminder(text)

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

    # Definition
    elif "define" in cmd or "definition" in cmd:
        word = cmd.replace("define ", "").replace("definition of ", "").replace("definition ", "")
        response["text"] = get_word_definition(word)

    # Translate
    elif "translate" in cmd:
        response["text"] = "To translate, say: translate [text] to [language], sir."

    # Crypto
    elif "bitcoin" in cmd or "crypto" in cmd or "ethereum" in cmd:
        coin = "bitcoin"
        if "ethereum" in cmd or "ether" in cmd:
            coin = "ethereum"
        elif "doge" in cmd:
            coin = "dogecoin"
        response["text"] = get_crypto_price(coin)

    # System info
    elif "system" in cmd and ("info" in cmd or "status" in cmd):
        response["text"] = "Retrieving system information, sir."
        response["data"] = {"type": "system", "info": system_info()}

    # IP address
    elif "ip address" in cmd or "my ip" in cmd:
        response["text"] = get_ip_info()

    # Time in timezone
    elif "time in" in cmd:
        tz = cmd.replace("time in ", "").replace("what time is it in ", "").strip()
        tz_map = {
            "london": "Europe/London", "new york": "America/New_York", "tokyo": "Asia/Tokyo",
            "dubai": "Asia/Dubai", "karachi": "Asia/Karachi", "lahore": "Asia/Karachi",
            "paris": "Europe/Paris", "sydney": "Australia/Sydney", "singapore": "Asia/Singapore",
            "los angeles": "America/Los_Angeles", "toronto": "America/Toronto"
        }
        tz_name = tz_map.get(tz, tz)
        response["text"] = get_time_in_timezone(tz_name)

    # Play music
    elif "play" in cmd and ("music" in cmd or "song" in cmd):
        song = cmd.replace("play ", "").replace("music", "").replace("song", "").strip()
        if song:
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            response["text"] = f"Playing {song} on YouTube, sir."
        else:
            webbrowser.open("https://www.youtube.com/results?search_query=music")
            response["text"] = "Opening YouTube music, sir."

    # Sleep
    elif "sleep" in cmd:
        if platform.system() == "Darwin":
            subprocess.run(["pmset", "sleepnow"], capture_output=True)
            response["text"] = "Goodnight, sir. System going to sleep."
        else:
            response["text"] = "Sleep only available on macOS."

    # Lock screen
    elif "lock" in cmd and "screen" in cmd or cmd == "lock":
        if platform.system() == "Darwin":
            subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
            response["text"] = "Locking the screen, sir."
        else:
            response["text"] = "Lock only available on macOS."

    # Empty trash
    elif "empty trash" in cmd or "clear trash" in cmd:
        if platform.system() == "Darwin":
            mac_applescript('tell application "Finder" to empty trash')
            response["text"] = "Emptying trash, sir."
        else:
            response["text"] = "Only available on macOS."

    # Calculate
    elif "calculate" in cmd or any(op in cmd for op in ["plus", "minus", "times", "divided"]):
        expr = cmd.replace("calculate ", "").replace("what is ", "").replace("what's ", "")
        expr = expr.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/").replace("x", "*")
        allowed = set("0123456789+-*/.() ")
        if all(c in allowed for c in expr):
            try:
                result = eval(expr)
                response["text"] = f"The answer is {result}, sir."
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
        response["text"] = "I can do 40+ things, sir. Check the skills panel on the left."

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
.header .logo { font-size: 14px; letter-spacing: 4px; color: #00aaff; opacity: 0.7; }
.header .status { font-size: 11px; color: #00ff88; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.status-listening .status-dot { background: #ffc800; animation: pulse 1s infinite; }
.status-thinking .status-dot { background: #9966ff; animation: pulse 0.5s infinite; }
.status-idle .status-dot { background: #00ff88; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
.reactor { position: relative; width: 300px; height: 300px; margin-top: 50px; display: flex; align-items: center; justify-content: center; }
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
.auto-mode { position: fixed; top: 50px; right: 20px; display: flex; align-items: center; gap: 8px; }
.auto-toggle { width: 40px; height: 22px; border-radius: 11px; background: rgba(0,170,255,0.2); border: 1px solid rgba(0,170,255,0.4); cursor: pointer; position: relative; }
.auto-toggle.on { background: rgba(0,255,136,0.3); border-color: #00ff88; }
.auto-toggle .knob { width: 16px; height: 16px; border-radius: 50%; background: #00aaff; position: absolute; top: 2px; left: 2px; transition: all 0.3s; }
.auto-toggle.on .knob { left: 20px; background: #00ff88; }
.auto-label { font-size: 11px; color: rgba(0,170,255,0.6); }
.skills-panel { position: fixed; top: 50px; left: 10px; width: 200px; max-height: 80vh; overflow-y: auto; padding: 5px; }
.skills-title { font-size: 10px; color: rgba(0,170,255,0.4); letter-spacing: 2px; margin-bottom: 8px; }
.skill-btn { padding: 6px 10px; margin-bottom: 4px; border-radius: 15px; background: rgba(0,170,255,0.05); border: 1px solid rgba(0,170,255,0.15); color: rgba(0,170,255,0.5); font-size: 10px; cursor: pointer; transition: all 0.2s; }
.skill-btn:hover { background: rgba(0,170,255,0.15); border-color: rgba(0,170,255,0.4); color: #00aaff; }
.conversation { position: fixed; top: 80px; right: 20px; width: 340px; max-height: 55vh; overflow-y: auto; padding: 5px; }
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
.data-display { position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 500px; max-height: 150px; overflow-y: auto; display: none; }
.data-display.active { display: block; }
.data-card { background: rgba(0,170,255,0.05); border: 1px solid rgba(0,170,255,0.2); border-radius: 8px; padding: 12px; margin-top: 4px; font-size: 11px; }
.data-card h4 { color: #00aaff; margin-bottom: 6px; font-size: 12px; }
.data-card pre { color: rgba(0,255,136,0.7); white-space: pre-wrap; font-size: 10px; }
</style>
</head>
<body>

<div class="header">
    <div class="logo">J.A.R.V.I.S v2.0</div>
    <div class="status status-idle" id="statusBar"><span class="status-dot"></span><span id="statusText">ONLINE</span></div>
</div>

<div class="auto-mode">
    <span class="auto-label">AUTO-LISTEN</span>
    <div class="auto-toggle on" id="autoToggle" onclick="toggleAutoListen()"><div class="knob"></div></div>
</div>

<div class="skills-panel">
    <div class="skills-title">SKILLS (40+)</div>
    <div class="skill-btn" onclick="sendCmd('what time is it')">Time</div>
    <div class="skill-btn" onclick="sendCmd('what is the date')">Date</div>
    <div class="skill-btn" onclick="sendCmd('weather in Lahore')">Weather</div>
    <div class="skill-btn" onclick="sendCmd('news')">Tech News</div>
    <div class="skill-btn" onclick="sendCmd('open youtube')">Open YouTube</div>
    <div class="skill-btn" onclick="sendCmd('open google')">Open Google</div>
    <div class="skill-btn" onclick="sendCmd('launch safari')">Launch Safari</div>
    <div class="skill-btn" onclick="sendCmd('launch notes')">Launch Notes</div>
    <div class="skill-btn" onclick="sendCmd('launch music')">Launch Music</div>
    <div class="skill-btn" onclick="sendCmd('launch mail')">Launch Mail</div>
    <div class="skill-btn" onclick="sendCmd('launch calculator')">Calculator</div>
    <div class="skill-btn" onclick="sendCmd('launch terminal')">Terminal</div>
    <div class="skill-btn" onclick="sendCmd('launch finder')">Finder</div>
    <div class="skill-btn" onclick="sendCmd('launch settings')">Settings</div>
    <div class="skill-btn" onclick="sendCmd('screenshot')">Screenshot</div>
    <div class="skill-btn" onclick="sendCmd('system info')">System Info</div>
    <div class="skill-btn" onclick="sendCmd('running apps')">Running Apps</div>
    <div class="skill-btn" onclick="sendCmd('volume up')">Volume Up</div>
    <div class="skill-btn" onclick="sendCmd('volume down')">Volume Down</div>
    <div class="skill-btn" onclick="sendCmd('open downloads')">Downloads</div>
    <div class="skill-btn" onclick="sendCmd('open desktop')">Desktop</div>
    <div class="skill-btn" onclick="sendCmd('open documents')">Documents</div>
    <div class="skill-btn" onclick="sendCmd('joke')">Joke</div>
    <div class="skill-btn" onclick="sendCmd('quote')">Quote</div>
    <div class="skill-btn" onclick="sendCmd('trivia')">Trivia</div>
    <div class="skill-btn" onclick="sendCmd('bitcoin price')">Bitcoin</div>
    <div class="skill-btn" onclick="sendCmd('my ip address')">IP Address</div>
    <div class="skill-btn" onclick="sendCmd('time in london')">Time in London</div>
    <div class="skill-btn" onclick="sendCmd('time in new york')">Time in NY</div>
    <div class="skill-btn" onclick="sendCmd('time in dubai')">Time in Dubai</div>
    <div class="skill-btn" onclick="sendCmd('note buy groceries')">Quick Note</div>
    <div class="skill-btn" onclick="sendCmd('remind call mom')">Reminder</div>
    <div class="skill-btn" onclick="sendCmd('lock screen')">Lock Mac</div>
    <div class="skill-btn" onclick="sendCmd('sleep')">Sleep Mac</div>
    <div class="skill-btn" onclick="sendCmd('empty trash')">Empty Trash</div>
    <div class="skill-btn" onclick="sendCmd('what is artificial intelligence')">Wikipedia</div>
    <div class="skill-btn" onclick="sendCmd('define computer')">Dictionary</div>
    <div class="skill-btn" onclick="sendCmd('play music')">Play Music</div>
    <div class="skill-btn" onclick="sendCmd('help')">All Skills</div>
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
let recognition = null;
let isListening = false;
let autoListen = true;
let wakeWordDetected = false;
let lastTranscript = '';

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
            // Check for wake word "jarvis"
            if (fullTranscript.includes('jarvis') || fullTranscript.includes('jeffrey') || fullTranscript.includes('travis')) {
                wakeWordDetected = true;
                setReactorState('listening');
                // Extract command after "jarvis"
                let command = fullTranscript.replace(/.*jarvis[, ]*/, '').replace(/.*jeffrey[, ]*/, '').replace(/.*travis[, ]*/, '').trim();
                if (command && isFinal) {
                    lastTranscript = command;
                    addMessage('user', command);
                    sendToJarvis(command);
                    wakeWordDetected = false;
                } else if (command) {
                    document.getElementById('commandInput').value = command;
                }
            } else if (wakeWordDetected && fullTranscript) {
                document.getElementById('commandInput').value = fullTranscript;
                if (isFinal) {
                    lastTranscript = fullTranscript;
                    addMessage('user', fullTranscript);
                    sendToJarvis(fullTranscript);
                    wakeWordDetected = false;
                }
            }
        } else {
            // Manual mode - use everything as command
            document.getElementById('commandInput').value = fullTranscript;
            if (isFinal && fullTranscript) {
                lastTranscript = fullTranscript;
                sendInput();
            }
        }
    };

    recognition.onerror = (e) => {
        console.log('Speech error:', e.error);
        if (e.error === 'no-speech' || e.error === 'aborted') {
            // Restart if in auto mode
            if (autoListen) setTimeout(startAutoListening, 1000);
        } else if (e.error === 'not-allowed') {
            addMessage('jarvis', 'Microphone access denied. Please allow microphone access in your browser settings, sir.');
        }
    };

    recognition.onend = () => {
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        if (autoListen) {
            // Auto-restart listening
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
        document.getElementById('bootText').textContent = 'Say "JARVIS" then your command, sir';
    } catch(e) {
        // Already started
    }
}

function toggleAutoListen() {
    autoListen = !autoListen;
    const toggle = document.getElementById('autoToggle');
    if (autoListen) {
        toggle.classList.add('on');
        startAutoListening();
        addMessage('jarvis', 'Auto-listening activated. Just say JARVIS followed by your command, sir.');
    } else {
        toggle.classList.remove('on');
        if (isListening) {
            recognition.stop();
        }
        addMessage('jarvis', 'Auto-listening disabled. Click the mic button to speak, sir.');
    }
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
        isListening = false;
        document.getElementById('micBtn').classList.remove('listening');
        setReactorState('idle');
    } else {
        try {
            recognition.start();
            isListening = true;
            document.getElementById('micBtn').classList.add('listening');
            setReactorState('listening');
        } catch(e) {}
    }
}

function setReactorState(state) {
    const reactor = document.getElementById('reactor');
    const core = document.getElementById('core');
    const boot = document.getElementById('bootText');
    const statusBar = document.getElementById('statusBar');

    reactor.classList.remove('reactor-listening', 'reactor-thinking');
    statusBar.classList.remove('status-idle', 'status-listening', 'status-thinking');

    if (state === 'listening') {
        reactor.classList.add('reactor-listening');
        statusBar.classList.add('status-listening');
        core.textContent = 'LISTEN';
        boot.textContent = 'I am listening, sir...';
        document.getElementById('statusText').textContent = 'LISTENING';
    } else if (state === 'thinking') {
        reactor.classList.add('reactor-thinking');
        statusBar.classList.add('status-thinking');
        core.textContent = 'PROC';
        boot.textContent = 'Processing, sir...';
        document.getElementById('statusText').textContent = 'PROCESSING';
    } else {
        statusBar.classList.add('status-idle');
        core.textContent = 'JARVIS';
        boot.textContent = 'Say "JARVIS" then your command, sir';
        document.getElementById('statusText').textContent = autoListen ? 'AUTO-LISTENING' : 'ONLINE';
    }
}

function sendCmd(cmd) {
    addMessage('user', cmd);
    sendToJarvis(cmd);
}

function sendInput() {
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    input.value = '';
    addMessage('user', cmd);
    sendToJarvis(cmd);
}

function sendToJarvis(command) {
    setReactorState('thinking');
    fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
    })
    .then(r => r.json())
    .then(data => {
        setReactorState('idle');
        addMessage('jarvis', data.text);
        speak(data.text);
        if (data.data) displayData(data.data);
    })
    .catch(e => {
        setReactorState('idle');
        addMessage('jarvis', 'Connection error, sir.');
    });
}

function addMessage(sender, text) {
    const conv = document.getElementById('conversation');
    const msg = document.createElement('div');
    msg.className = 'msg ' + sender;
    msg.innerHTML = '<div class="label">' + (sender === 'user' ? 'YOU' : 'JARVIS') + '</div>' + text;
    conv.appendChild(msg);
    conv.scrollTop = conv.scrollHeight;
}

function speak(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 0.95;
        utter.pitch = 0.85;
        utter.volume = 0.8;
        const voices = speechSynthesis.getVoices();
        const preferred = voices.find(v => v.name.includes('Daniel') || v.name.includes('Arthur') || v.name.includes('Oliver') || (v.lang === 'en-GB' && v.name.includes('Google')));
        if (preferred) utter.voice = preferred;
        speechSynthesis.speak(utter);
    }
}

function displayData(data) {
    const display = document.getElementById('dataDisplay');
    if (data.type === 'system') {
        display.innerHTML = '<div class="data-card"><h4>SYSTEM INFO</h4><pre>' + data.info + '</pre></div>';
        display.classList.add('active');
    } else if (data.type === 'clear') {
        document.getElementById('conversation').innerHTML = '';
        display.classList.remove('active');
    } else if (data.type === 'shutdown_jarvis') {
        setTimeout(() => { window.close(); }, 2000);
    }
}

// Boot
setTimeout(() => {
    addMessage('jarvis', 'JARVIS v2.0 online. Auto-listening is ON. Just say JARVIS followed by your command, sir.');
    speak('JARVIS version 2.0 online. Auto listening is on. Just say JARVIS followed by your command, sir.');
    // Start auto-listening
    setTimeout(startAutoListening, 1000);
}, 800);

// Load voices
if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = () => {};
    speechSynthesis.getVoices();
}
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
    print("  J.A.R.V.I.S v2.0 - Starting...")
    print("  Auto-listening is ON")
    print("  Say 'JARVIS' then your command")
    print("  Open browser: http://localhost:7654")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    webbrowser.open("http://localhost:7654")
    app.run(host='0.0.0.0', port=7654, debug=False)
