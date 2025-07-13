import speech_recognition as sr
import pycountry

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
        print(f"🎤 {player}, say a country:")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("⌛ You took too long to start speaking. Please try again.")
            return None
    try:
        country = recognizer.recognize_google(audio)
        print(f"🗣️ {player} said: {country}")
        return country
    except sr.UnknownValueError:
        print("❌ Could not understand. Try again.")
        return None
    except sr.RequestError:
        print("🔌 Could not request results; check your internet connection.")
        return None

def check_country(player, country):
    country_clean = country.strip().lower()

    if country_clean in alternative_names:
        country_clean = alternative_names[country_clean]

    if country_clean not in valid_countries:
        print(f"❌ '{country}' is not a recognized country. Please try again.")
        return None  # Invalid country, ask player again

    if country_clean in used_countries:
        warnings[player] += 1
        print(f"⚠️ Warning {warnings[player]} for {player}! '{country_clean.title()}' was already said before.")
        if warnings[player] >= 3:
            print(f"❌ {player} has reached 3 warnings and lost the game. Game over.")
            return False  # Player lost
        else:
            # Warning issued, player must try again
            return None

    used_countries.add(country_clean)
    print(f"✅ {player} accepted: {country_clean.title()}")
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
