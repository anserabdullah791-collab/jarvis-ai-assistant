# J.A.R.V.I.S — AI Assistant

Just A Rather Very Intelligent System — inspired by Iron Man.

## What is this?
A complete AI assistant that runs on your MacBook. Voice commands + text commands. No complex setup. No hardware needed.

## Features
1. Voice recognition (speak commands) — uses browser Web Speech API
2. Text-to-speech (JARVIS talks back) — uses browser speech synthesis
3. Time and date
4. Weather (any city in the world)
5. Tech news
6. Open websites (YouTube, Google, Facebook, etc.)
7. Open Mac apps (Safari, Notes, Music, etc.)
8. Wikipedia search
9. Jokes
10. Math calculations
11. System information (CPU, RAM, OS)
12. IP address info
13. Screenshots (macOS)
14. Volume control (macOS)
15. Play music (YouTube search)
16. System sleep/lock (macOS)
17. Beautiful JARVIS reactor UI with animations
18. Conversation history panel
19. Quick command buttons

## Setup (3 steps)

### Step 1: Install Python
macOS usually has Python3 pre-installed. If not:
```
brew install python
```

### Step 2: Download
```
git clone https://github.com/anserabdullah791-collab/jarvis-ai-assistant.git
cd jarvis-ai-assistant
```

### Step 3: Run
Double-click `start_jarvis.command`

OR run manually:
```
pip3 install flask requests
python3 jarvis.py
```

Then open: http://localhost:7654

## How to use

### Voice Commands
Click the microphone icon and speak:
- "What time is it"
- "Weather in Lahore"
- "Open YouTube"
- "Tell me a joke"
- "What is artificial intelligence"
- "Play music"
- "System info"
- "News"

### Text Commands
Type in the command bar and press Enter.

### Quick Commands
Click any button on the left panel for instant actions.

## Browser Support
- Safari (macOS) — full voice support
- Chrome — full voice support
- Firefox — text commands only (no voice)

## Note
- Uses free APIs (Open-Meteo weather, Hacker News, Wikipedia) — no API keys needed
- Works offline for basic commands (time, date, system info)
- Voice recognition requires internet connection
- For best experience, use Safari or Chrome on macOS

## Future Features (Roadmap)
- OpenAI integration for conversational AI
- Smart home control
- Calendar integration
- Email sending
- Face recognition
- Custom wake word "Jarvis"
- Mobile app version
