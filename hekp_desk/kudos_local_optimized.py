
# Architecture:
#
#   Microphone
#       ↓
#   Speech Recognition
#       ↓
#   Kudos Assistant
#       ↓ HTTP
#   Local AI API
#       ↓
#   Ollama
#       ↓
#   qwen2.5:1.5b
#       ↓
#   Response
#       ↓
#   Text To Speech
#
# The LLM provider is isolated so it can later be changed
# from Ollama → College Server → OpenAI-compatible API, etc.
# ============================================================
import requests
import pyttsx3
import os
import threading
import wave
import speech_recognition as sr
import webbrowser
from youtubesearchpython import VideosSearch
import pygame

from colorama import Fore, Style
import json
import vosk
import sounddevice as sd
import time
try:
    from piper import PiperVoice, SynthesisConfig
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False


# ============================================================
# CONFIGURATION
# ============================================================

AI_PROVIDER = "ollama"
OFFLINE_MODE = True

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:1.5b"

# Later you can change this to:
#
# AI_PROVIDER = "remote"
#
# and point it to your college AI server.
REMOTE_AI_URL = "http://127.0.0.1:8000/chat"
# ============================================================
# LOCAL SPEECH RECOGNITION - VOSK
# ============================================================

VOSK_MODEL_CANDIDATES = [
    "vosk-model-en-us-0.22",
    "vosk-model-small-en-us-0.15"
]

VOSK_MODEL_PATH = next(
    (
        path
        for path in VOSK_MODEL_CANDIDATES
        if os.path.isdir(path)
    ),
    None
)

if VOSK_MODEL_PATH is None:
    raise FileNotFoundError(
        "No Vosk model found. "
        "Place vosk-model-en-us-0.22 or "
        "vosk-model-small-en-us-0.15 in the project directory."
    )

print(
    Fore.GREEN +
    f"Vosk model: {VOSK_MODEL_PATH}" +
    Style.RESET_ALL
)
# Piper neural TTS voice. Download once, then it works fully offline.
PIPER_MODEL_PATH = "en_US-amy-medium.onnx"
PIPER_CONFIG_PATH = "en_US-amy-medium.onnx.json"

# Audio / recognition tuning
MIC_SAMPLE_RATE = 16000
WAKE_MAX_SECONDS = 4
COMMAND_TIMEOUT = 6
COMMAND_MAX_SECONDS = 12

# Load the Vosk model once. Do NOT reload it for every sentence.
vosk_model = vosk.Model(VOSK_MODEL_PATH)

# Separate small grammar for the wake word. This is faster and less sensitive
# to random background speech than unrestricted recognition.
WAKE_GRAMMAR = json.dumps([
    "kudos",
    "hey kudos",
    "okay kudos",
    "ok kudos",
    "[unk]"
])

wake_vosk_recognizer = vosk.KaldiRecognizer(
    vosk_model,
    MIC_SAMPLE_RATE,
    WAKE_GRAMMAR
)

speech_vosk_recognizer = vosk.KaldiRecognizer(
    vosk_model,
    MIC_SAMPLE_RATE
)

# Load Piper once. Loading a neural TTS model every time speak() runs would
# destroy responsiveness. If Piper is unavailable, pyttsx3 remains as fallback.
piper_voice = None
if PIPER_AVAILABLE and os.path.exists(PIPER_MODEL_PATH):
    try:
        piper_voice = PiperVoice.load(PIPER_MODEL_PATH)
        print(Fore.GREEN + "Piper TTS: enabled" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.YELLOW + f"Piper TTS unavailable: {e}" + Style.RESET_ALL)
else:
    print(Fore.YELLOW + "Piper voice not found; using pyttsx3 fallback." + Style.RESET_ALL)

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Kudos, a college robot assistant.

Be helpful, natural, concise and professional.
Answer normal questions in one or two short sentences.
Do not use markdown or emojis.
Do not repeat the user's question.
Only provide detailed explanations when explicitly requested.
"""

# ============================================================
# INITIALIZE AUDIO
# ============================================================

# Pygame is initialized lazily only when a predefined MP3 is played.
# This avoids initializing an unnecessary ALSA mixer at startup.
pygame_initialized = False


# ============================================================
# TEXT TO SPEECH
# ============================================================

# Keep pyttsx3 only as a safe fallback. Piper is the primary voice.
engine = None
if piper_voice is None:
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

speaking = False
speak_lock = threading.Lock()


def speak(text):
    """Fast local neural TTS with pyttsx3 fallback."""
    global speaking

    text = clean_response(text)
    if not text:
        return

    with speak_lock:
        speaking = True

        print(
            Fore.CYAN +
            "Kudos: " +
            text +
            Style.RESET_ALL
        )

        try:
            if piper_voice is not None:
                # Slightly faster than default while retaining natural timing.
                syn_config = SynthesisConfig(
                    length_scale=0.95,
                    noise_scale=0.667,
                    noise_w_scale=0.8,
                    normalize_audio=True
                )

                stream = None
                try:
                    for chunk in piper_voice.synthesize(text, syn_config=syn_config):
                        if stream is None:
                            stream = sd.RawOutputStream(
                                samplerate=chunk.sample_rate,
                                channels=chunk.sample_channels,
                                dtype="int16",
                                latency="low"
                            )
                            stream.start()
                        stream.write(chunk.audio_int16_bytes)
                finally:
                    if stream is not None:
                        stream.stop()
                        stream.close()
            else:
                engine.say(text)
                engine.runAndWait()

        except Exception as e:
            print(
                Fore.RED +
                f"TTS error: {e}" +
                Style.RESET_ALL
            )

        finally:
            speaking = False


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 400

recognizer.dynamic_energy_threshold = False

recognizer.pause_threshold = 0.65

recognizer.phrase_threshold = 0.25

recognizer.non_speaking_duration = 0.35


# ============================================================
# AUDIO RESPONSES
# ============================================================

audio_responses = {

    "how are you":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\thank_you_for_asking.mp3",

    "what is your name":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\I'm_kudos.mp3",

    "how is the weather":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\how_is_the_weather.mp3",

    "who created you":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\made_by.mp3",

    "aapka kya naam hai":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\mera_naam.mp3",

    "pakistan ka matlab kya":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\la_illah.mp3",

    "gilgit baltistan ke bare mein bataen":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\gb.mp3",

    "uswa ke bare mein bataen":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\uswa_barey.mp3",

    "pakistan ke bare mein bataen":
        r"D:\Work Space\Programming\PYTHON\Project AI\Assistant\AI-PRED\pakistan.mp3"
}


def play_audio(file_path):

    global pygame_initialized

    try:
        if not pygame_initialized:
            pygame.mixer.init()
            pygame_initialized = True

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:

        print(
            Fore.RED +
            f"Audio error: {e}" +
            Style.RESET_ALL
        )


# ============================================================
# PREDEFINED QUESTIONS
# ============================================================

def handle_specific_questions(question):

    question_lower = question.lower().strip()

    if question_lower in audio_responses:

        play_audio(audio_responses[question_lower])

        print(
            Fore.GREEN +
            f"Playing predefined response for '{question_lower}'" +
            Style.RESET_ALL
        )

        return True

    return False



# ============================================================
# WEB FUNCTIONS
# ============================================================

def open_website(site_name):

    if OFFLINE_MODE:
        speak("Offline mode is enabled, so web access is disabled.")
        return True

    site_name = site_name.strip()

    if not site_name.startswith("http://") and \
       not site_name.startswith("https://"):

        site_name = site_name.replace(" ", "")
        site_name = "https://" + site_name + ".com"

    webbrowser.open(site_name)

    return True


def search_google(query):

    if OFFLINE_MODE:
        speak("Offline mode is enabled, so web search is disabled.")
        return True

    search_url = (
        "https://www.google.com/search?q=" +
        query.replace(" ", "+")
    )

    webbrowser.open(search_url)

    print(
        Fore.GREEN +
        f"Searching Google for {query}" +
        Style.RESET_ALL
    )

    speak(f"Searching Google for {query}")

    return True


def play_youtube_video(query):

    if OFFLINE_MODE:
        speak("Offline mode is enabled, so YouTube is disabled.")
        return True

    try:

        videos_search = VideosSearch(
            query,
            limit=1
        )

        result = videos_search.result()

        if not result["result"]:
            speak("I could not find that video.")
            return True

        video_url = result["result"][0]["link"]

        print(
            Fore.GREEN +
            f"Playing {query}" +
            Style.RESET_ALL
        )

        speak(f"Playing {query}")

        webbrowser.open(video_url)

        return True

    except Exception as e:

        print(
            Fore.RED +
            f"YouTube error: {e}" +
            Style.RESET_ALL
        )

        speak("I could not play that video.")

        return True


# ============================================================
# FEATURE COMMANDS
# ============================================================

def respond_with_features(voice_data):

    voice_data_lower = voice_data.lower().strip()


    # --------------------------------------------------------
    # Predefined audio responses
    # --------------------------------------------------------

    if handle_specific_questions(voice_data_lower):
        return True


    # --------------------------------------------------------
    # Open website
    # --------------------------------------------------------

    if voice_data_lower.startswith("open "):

        site_name = (
            voice_data_lower
            .replace("open ", "", 1)
            .strip()
        )

        if open_website(site_name):

            speak(f"Opening {site_name}")

            return True


    # --------------------------------------------------------
    # YouTube
    # --------------------------------------------------------

    if voice_data_lower.startswith("play "):

        search_query = (
            voice_data_lower
            .replace("play ", "", 1)
            .strip()
        )

        return play_youtube_video(search_query)


    # --------------------------------------------------------
    # Google search
    # --------------------------------------------------------

    if voice_data_lower.startswith("search "):

        search_query = (
            voice_data_lower
            .replace("search ", "", 1)
            .strip()
        )

        return search_google(search_query)


    return False


# ============================================================
# LOCAL OLLAMA API
# ============================================================
def ask_ollama(user_message, conversation):

    payload = {
    "model": OLLAMA_MODEL,
    "messages": conversation,
    "stream": False,
    "keep_alive": -1,

    "options": {
        "temperature": 0.4,
        "top_p": 0.85,
        "num_predict": 32,
    }
}

    try:

        start_time = time.perf_counter()

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=45
        )

        response.raise_for_status()

        data = response.json()

        message = data["message"]["content"].strip()

        elapsed = time.perf_counter() - start_time

        print(
            Fore.MAGENTA +
            f"Ollama response time: {elapsed:.2f}s" +
            Style.RESET_ALL
        )

        return message

    except requests.exceptions.ConnectionError:

        return (
            "I cannot connect to the local AI server. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "The local AI model is taking too long to respond."
        )

    except Exception as e:

        print(
            Fore.RED +
            f"Ollama error: {e}" +
            Style.RESET_ALL
        )

        return "I encountered an error while processing your request."

# ============================================================
# FUTURE REMOTE AI API
# ============================================================

def ask_remote_api(user_message, conversation):

    payload = {

        "message": user_message,

        "conversation": conversation
    }


    try:

        response = requests.post(
            REMOTE_AI_URL,
            json=payload,
            timeout=45
        )


        response.raise_for_status()


        data = response.json()


        return data["response"].strip()


    except requests.exceptions.ConnectionError:

        return "I cannot connect to the college AI server."


    except Exception as e:

        print(
            Fore.RED +
            f"Remote API error: {e}" +
            Style.RESET_ALL
        )

        return "The AI server encountered an error."


# ============================================================
# AI PROVIDER ROUTER
# ============================================================

def ask_ai(user_message, conversation):

    if AI_PROVIDER == "ollama":

        return ask_ollama(
            user_message,
            conversation
        )


    elif AI_PROVIDER == "remote":

        return ask_remote_api(
            user_message,
            conversation
        )


    else:

        return "No AI provider has been configured."


# ============================================================
# CONVERSATION MEMORY
# ============================================================

conversation = [

    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }

]


# ============================================================
# AI RESPONSE
# ============================================================

def generate_response(question):

    global conversation


    # Add user message

    conversation.append({

        "role": "user",

        "content": question

    })


    response = ask_ai(
        question,
        conversation
    )


    # Add AI response

    conversation.append({

        "role": "assistant",

        "content": response

    })


    # Prevent unlimited memory growth
    #
    # Keep system prompt + last 10 messages.

    if len(conversation) > 9:

        conversation = [
            conversation[0]
        ] + conversation[-4:]


    return response


# ============================================================
# CLEAN RESPONSE
# ============================================================

def clean_response(text):

    text = text.replace("*", "")
    text = text.replace("#", "")
    text = text.replace("```", "")

    return text.strip()


# ============================================================
# LOCAL VOSK SPEECH-TO-TEXT
# ============================================================
def recognize_vosk(audio, wake_word=False):

    try:

        raw_audio = audio.get_raw_data(
            convert_rate=MIC_SAMPLE_RATE,
            convert_width=2
        )

        stt = (
            wake_vosk_recognizer
            if wake_word
            else speech_vosk_recognizer
        )

        stt.Reset()

        # Feed Vosk reasonably sized chunks.
        chunk_size = 4000

        for start in range(
            0,
            len(raw_audio),
            chunk_size
        ):

            chunk = raw_audio[
                start:start + chunk_size
            ]

            stt.AcceptWaveform(chunk)

        result = json.loads(
            stt.FinalResult()
        )

        text = result.get(
            "text",
            ""
        ).strip().lower()

        if not text:
            return ""

        return text

    except Exception as e:

        print(
            Fore.RED +
            f"Vosk error: {e}" +
            Style.RESET_ALL
        )

        return ""
def calibrate_microphone(source):

    print(
        Fore.YELLOW +
        "Calibrating microphone... stay quiet." +
        Style.RESET_ALL
    )

    recognizer.adjust_for_ambient_noise(
        source,
        duration=1.5
    )

    # Don't let the threshold continuously chase your voice.
    recognizer.dynamic_energy_threshold = False

    print(
        Fore.GREEN +
        f"Microphone ready "
        f"(threshold={recognizer.energy_threshold:.0f})" +
        Style.RESET_ALL
    )
# ============================================================
# LISTEN FOR ACTIVATION WORD
# ============================================================
def listen_for_kudos():

    with sr.Microphone(sample_rate=MIC_SAMPLE_RATE) as source:

        print(
            Fore.YELLOW +
            "Waiting for 'Kudos'..." +
            Style.RESET_ALL
        )

        # Calibrate once for this microphone session.
        calibrate_microphone(source)

        while True:
            try:
                audio = recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=WAKE_MAX_SECONDS
                )

                keyword = recognize_vosk(audio, wake_word=True)

                if keyword:
                    print(
                        Fore.WHITE +
                        "Heard: " +
                        keyword +
                        Style.RESET_ALL
                    )

                if "kudos" in keyword:
                    print(
                        Fore.GREEN +
                        "'Kudos' detected!" +
                        Style.RESET_ALL
                    )

                    speak("Yes, how can I assist you?")
                    handle_conversation(source)

            except Exception as e:
                print(
                    Fore.RED +
                    f"Wake-word error: {e}" +
                    Style.RESET_ALL
                )

# ============================================================
# MAIN CONVERSATION
# ============================================================

def handle_conversation(source):

    global speaking

    # Reuse the already-open microphone. No second PyAudio device is opened.
    while True:

        print(
            Fore.YELLOW +
            "Listening..." +
            Style.RESET_ALL
        )

        try:
            audio = recognizer.listen(
                source,
                timeout=COMMAND_TIMEOUT,
                phrase_time_limit=COMMAND_MAX_SECONDS
            )

            question = recognize_vosk(audio)
            question = question.strip()

            if not question:
                print(
                    Fore.RED +
                    "Could not understand audio." +
                    Style.RESET_ALL
                )
                continue

            print(
                Fore.GREEN +
                "You: " +
                question +
                Style.RESET_ALL
            )

            if question.lower() in [
                "exit",
                "goodbye",
                "bye",
                "quit"
            ]:
                speak("Goodbye!")
                return

            if (
                "stop speaking" in question.lower()
                and speaking
            ):
                if engine is not None:
                    engine.stop()
                speaking = False
                return

            if respond_with_features(question):
                continue

            print(
                Fore.YELLOW +
                "Kudos is thinking..." +
                Style.RESET_ALL
            )

            response = generate_response(question)
            response = clean_response(response)

            detailed_keywords = [
                "detailed",
                "long",
                "detail",
                "explain in detail",
                "explain fully"
            ]

            if any(
                keyword in question.lower()
                for keyword in detailed_keywords
            ):
                speak(response)
            else:
                sentences = response.split(". ")
                short_response = sentences[0]

                if not short_response.endswith("."):
                    short_response += "."

                speak(short_response)

        except sr.WaitTimeoutError:
            continue

        except Exception as e:
            print(
                Fore.RED +
                f"Conversation error: {e}" +
                Style.RESET_ALL
            )

# ============================================================
# STARTUP
# ============================================================

print()
print("=" * 60)

print(
    Fore.CYAN +
    "             KUDOS LOCAL AI" +
    Style.RESET_ALL
)

print("=" * 60)

print()

print(
    Fore.WHITE +
    "AI Provider : " +
    Fore.GREEN +
    AI_PROVIDER +
    Style.RESET_ALL
)

print(
    Fore.WHITE +
    "Model       : " +
    Fore.GREEN +
    OLLAMA_MODEL +
    Style.RESET_ALL
)

print(
    Fore.WHITE +
    "Ollama API  : " +
    Fore.GREEN +
    OLLAMA_URL +
    Style.RESET_ALL
)

print()

print(
    Fore.YELLOW +
    "Say 'Kudos' to activate the assistant." +
    Style.RESET_ALL
)

print(
    Fore.YELLOW +
    "Say 'exit' to end a conversation." +
    Style.RESET_ALL
)

print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    listen_for_kudos()