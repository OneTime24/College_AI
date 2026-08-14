# ============================================================
# KUDOS - LOCAL AI VOICE ASSISTANT
# ============================================================
#
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
import speech_recognition as sr
import webbrowser
from youtubesearchpython import VideosSearch
import pygame

from colorama import Fore, Style


# ============================================================
# CONFIGURATION
# ============================================================

AI_PROVIDER = "ollama"

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:1.5b"

# Later you can change this to:
#
# AI_PROVIDER = "remote"
#
# and point it to your college AI server.
REMOTE_AI_URL = "http://127.0.0.1:8000/chat"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Kudos, an AI assistant installed in a college robot.

Your personality:
- Helpful
- Intelligent
- Natural
- Concise
- Friendly
- Professional

Rules:
- Give direct answers.
- Do not unnecessarily explain things.
- Do not use markdown unless necessary.
- Do not use emojis.
- Do not mention that you are an AI language model unless asked.
- Keep normal answers short.
- If the user explicitly asks for a detailed explanation, provide more detail.
- Answer naturally as if speaking to a person.
"""


# ============================================================
# INITIALIZE AUDIO
# ============================================================

pygame.mixer.init()


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()

voices = engine.getProperty("voices")

if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)

engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

speaking = False


def speak(text):
    global speaking

    speaking = True

    print(
        Fore.CYAN +
        "Kudos: " +
        text +
        Style.RESET_ALL
    )

    engine.say(text)
    engine.runAndWait()

    speaking = False


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8


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

    try:

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

    site_name = site_name.strip()

    if not site_name.startswith("http://") and \
       not site_name.startswith("https://"):

        site_name = site_name.replace(" ", "")
        site_name = "https://" + site_name + ".com"

    webbrowser.open(site_name)

    return True


def search_google(query):

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

        "options": {

            "temperature": 0.5,

            "top_p": 0.9,

            "num_predict": 300
        }
    }


    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )


        response.raise_for_status()


        data = response.json()


        message = data["message"]["content"]


        return message.strip()


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
            timeout=120
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

    if len(conversation) > 21:

        conversation = [
            conversation[0]
        ] + conversation[-20:]


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
# LISTEN FOR ACTIVATION WORD
# ============================================================

def listen_for_kudos():

    with sr.Microphone() as source:

        print(
            Fore.YELLOW +
            "Waiting for 'Kudos'..." +
            Style.RESET_ALL
        )

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )


        try:

            audio = recognizer.listen(
                source,
                timeout=None
            )


            keyword = recognizer.recognize_google(
                audio
            )


            print(
                Fore.WHITE +
                "Heard: " +
                keyword +
                Style.RESET_ALL
            )


            if "kudos" in keyword.lower():

                print(
                    Fore.GREEN +
                    "'Kudos' detected!" +
                    Style.RESET_ALL
                )

                speak(
                    "Yes, how can I assist you?"
                )

                handle_conversation()


        except sr.UnknownValueError:

            pass


        except sr.RequestError as e:

            print(
                Fore.RED +
                f"Speech recognition error: {e}" +
                Style.RESET_ALL
            )


# ============================================================
# MAIN CONVERSATION
# ============================================================

def handle_conversation():

    global speaking


    while True:

        with sr.Microphone() as source:

            print(
                Fore.YELLOW +
                "Listening..." +
                Style.RESET_ALL
            )


            try:

                audio = recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=20
                )


                question = recognizer.recognize_google(
                    audio
                )


                question = question.strip()


                print(
                    Fore.GREEN +
                    "You: " +
                    question +
                    Style.RESET_ALL
                )


                # ------------------------------------------------
                # Exit
                # ------------------------------------------------

                if question.lower() in [
                    "exit",
                    "goodbye",
                    "bye",
                    "quit"
                ]:

                    speak("Goodbye!")

                    return


                # ------------------------------------------------
                # Stop speaking
                # ------------------------------------------------

                if (
                    "stop speaking" in question.lower()
                    and speaking
                ):

                    engine.stop()

                    speaking = False

                    return


                # ------------------------------------------------
                # Local feature commands
                # ------------------------------------------------

                if respond_with_features(question):

                    continue


                # ------------------------------------------------
                # AI
                # ------------------------------------------------

                print(
                    Fore.YELLOW +
                    "Kudos is thinking..." +
                    Style.RESET_ALL
                )


                response = generate_response(
                    question
                )


                response = clean_response(
                    response
                )


                # ------------------------------------------------
                # Detailed response
                # ------------------------------------------------

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

                    # Keep normal responses short.

                    sentences = response.split(". ")

                    short_response = sentences[0]

                    if not short_response.endswith("."):
                        short_response += "."


                    speak(short_response)


            except sr.UnknownValueError:

                print(
                    Fore.RED +
                    "Could not understand audio." +
                    Style.RESET_ALL
                )


            except sr.RequestError as e:

                print(
                    Fore.RED +
                    f"Speech recognition error: {e}" +
                    Style.RESET_ALL
                )


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