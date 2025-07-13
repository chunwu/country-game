import speech_recognition as sr
from rapidfuzz import process, fuzz
import pycountry
import re
import os
import threading
import time

# Prep country lists
valid_countries = {country.name.lower(): country.name for country in pycountry.countries}
alternative_names = {
    "usa": "united states", "us": "united states",
    "uk": "united kingdom", "russia": "russian federation",
    "czech republic": "czechia", "south korea": "korea, republic of",
    "north korea": "korea, democratic people's republic of",
    "laos": "lao people's democratic republic",
    "vietnam": "viet nam", "ivory coast": "côte d’ivoire"
}
for alt, official in alternative_names.items():
    valid_countries[alt] = official

# Game state
used_countries = set()
warnings = {"Player 1": 0, "Player 2": 0}
player_turn = [0]  # mutable so it can be modified in background
players = ["Player 1", "Player 2"]

# Setup recognizer and mic
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Play tone helpers (you already have these)
def play_tone_accepted():
    os.system("afplay sms.mp3")  # or use playsound()

def play_tone_said():
    os.system("afplay mail.mp3")

# 🔍 Fuzzy country match
def fuzzy_match_country(phrase):
    phrase = re.sub(r"[^\w\s]", "", phrase.lower())

    result = process.extractOne(
        phrase,
        valid_countries.keys(),
        scorer=fuzz.partial_ratio,
        score_cutoff=80
    )

    if result:
        match, score, _ = result  # extractOne returns (match, score, index)
        return valid_countries[match]
    else:
        return None


# 🔄 Game logic
def handle_phrase(recognized_text):
    current_player = players[player_turn[0] % 2]
    print(f"\n🗣️ {current_player} said: {recognized_text}")

    country_name = fuzzy_match_country(recognized_text)
    if not country_name:
        print("❌ No valid country found in phrase.")
        return

    country_key = country_name.lower()
    if country_key in used_countries:
        warnings[current_player] += 1
        print(f"⚠️ Warning {warnings[current_player]} for {current_player}! '{country_name}' already used.")
        play_tone_said()
        if warnings[current_player] >= 3:
            print(f"❌ {current_player} lost the game with 3 warnings.")
            os._exit(0)
        return

    used_countries.add(country_key)
    print(f"✅ {current_player} accepted: {country_name}")
    play_tone_accepted()
    player_turn[0] += 1  # advance turn

# 🎧 Background callback
def callback(recognizer, audio):
    try:
        phrase = recognizer.recognize_google(audio)
        handle_phrase(phrase)
    except sr.UnknownValueError:
        print("🤷 Could not understand. Try again.")
    except sr.RequestError:
        print("🔌 Network error with speech recognition.")

def listen_loop():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("\n🎤 Listening started. Say a country on your turn...")

        while True:
            current_player = players[player_turn[0] % 2]
            print(f"\n🎙️ {current_player}, your turn. Speak naturally...")

            try:
                audio = recognizer.listen(
                    source,
                    timeout=30,           # Wait up to 30 sec to begin speaking
                    phrase_time_limit=25  # Allow up to 25 sec of speech
                )
            except sr.WaitTimeoutError:
                print("⌛ No speech detected. Please try again.")
                continue

            try:
                phrase = recognizer.recognize_google(audio)
                handle_phrase(phrase)
            except sr.UnknownValueError:
                print("🤷 Could not understand. Please try again.")
            except sr.RequestError:
                print("🔌 Network error with speech recognition.")


# 🏁 Start game
def start_game():
    print("🎮 Starting Country Game...")
    t = threading.Thread(target=listen_loop)
    t.daemon = True
    t.start()

    # Keep main thread alive
    while True:
        time.sleep(0.1)


start_game()
