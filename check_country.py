import speech_recognition as sr
import pycountry

from playsound import playsound
import os

def play_tone_accepted():
    os.system("afplay sms.mp3")  # or .wav

def play_tone_said():
    os.system("afplay mail.mp3")

def play_tone_not_recognized():
    os.system("afplay car-lock.mp3")

used_countries = set()
warnings = {"Player 1": 0, "Player 2": 0}
recognizer = sr.Recognizer()
mic = sr.Microphone()

valid_countries = {country.name.lower() for country in pycountry.countries}
alternative_names = {
    "usa": "united states",
    "uk": "united kingdom",
    "south korea": "korea, republic of",
    "north korea": "korea, democratic people's republic of",
    "russia": "russian federation",
    "venezuela": "venezuela, bolivarian republic of",
    "laos": "lao people's democratic republic",
    "czech republic": "czechia",
    "ivory coast": "côte d’ivoire",
    "vietnam": "viet nam",
}
for alt, official in alternative_names.items():
    valid_countries.add(alt)

def listen_for_country(player):
    with mic as source:
        print(f"\n🎤 {player}, say a country (you can speak naturally)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # Increase time to start speaking and allow longer phrases
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            print("⌛ You took too long to start speaking. Please try again.")
            return None

    try:
        country_phrase = recognizer.recognize_google(audio)
        print(f"🗣️ {player} said: {country_phrase}")
        return country_phrase
    except sr.UnknownValueError:
        print("🤷 Could not fully understand. If you said a country, try again a bit more clearly.")
        return None
    except sr.RequestError:
        print("🔌 Speech service unavailable. Check your internet connection.")
        return None


import re  # Make sure this is at the top of your file

def check_country(player, phrase):
    phrase_lower = phrase.lower()
    phrase_clean = re.sub(r"[^\w\s]", "", phrase_lower)  # Remove punctuation

    # Try to find a valid country name in the phrase
    country_name = None
    for name in alternative_names:
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, phrase_clean):
            country_name = alternative_names[name]
            break

    if not country_name:
        for name in valid_countries:
            pattern = r"\b" + re.escape(name) + r"\b"
            if re.search(pattern, phrase_clean):
                country_name = name
                break

    if not country_name:
        print(f"❌ No recognized country found in '{phrase}'. Please try again.")
        play_tone_not_recognized()
        return None

    country_clean = country_name.lower()

    if country_clean in used_countries:
        warnings[player] += 1
        print(f"⚠️ Warning {warnings[player]} for {player}! '{country_name.title()}' was already said before.")
        play_tone_said()
        if warnings[player] >= 3:
            print(f"❌ {player} has reached 3 warnings and lost the game. Game over.")
            return False  # Player lost
        else:
            return None  # Allow retry

    used_countries.add(country_clean)
    print(f"✅ {player} accepted: {country_name.title()}")
    play_tone_accepted()

    return True


def start_game():
    turn = 0
    print("🌍 Starting the Country Game (voice input + validation + warnings)...")
    print("🎯 Rule: Say a real country name. No repeats. 3 warnings = game over.")
    while True:
        player = "Player 1" if turn % 2 == 0 else "Player 2"
        while True:
            country = listen_for_country(player)
            if country is None:
                continue
            result = check_country(player, country)
            if result is None:
                # Player said invalid or repeated country and must try again
                continue
            elif result is False:
                # Player lost due to warnings
                return
            else:
                # Valid country, move on to next player
                break
        turn += 1

start_game()
