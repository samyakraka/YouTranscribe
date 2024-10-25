import os
import json
import yt_dlp
from moviepy.editor import AudioFileClip
import speech_recognition as sr
from gtts import gTTS
import streamlit as st
from googletrans import LANGUAGES, Translator
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from fpdf import FPDF

translator = Translator()

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def detect_language(text):
    """Detect the language of the provided text using Google Translate."""
    try:
        lang = translator.detect(text)
        return lang.lang  # Return the language code
    except Exception as e:
        st.error(f"Language detection error: {e}")
        return None

def download_youtube_audio(video_url, output_audio_path="audio.webm"):
    """Download the audio from a YouTube video."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_audio_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return output_audio_path
    except Exception as e:
        st.error(f"An error occurred during download: {e}")
        return None

def convert_to_wav(audio_path, output_wav_path="temp_audio.wav"):
    """Convert the downloaded audio to WAV format for compatibility."""
    try:
        audio_clip = AudioFileClip(audio_path)
        audio_clip.write_audiofile(output_wav_path, codec='pcm_s16le')
        return output_wav_path
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None

def extract_text_from_audio(wav_path, language='en-US'):
    """Transcribe audio from a WAV file using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Request error: {e}")
        return None

def translator_function(spoken_text, from_language, to_language):
    """Translate text using Google Translate."""
    try:
        translated = translator.translate(spoken_text, src=from_language, dest=to_language)
        return translated.text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

def text_to_voice(text_data, to_language, output_file="translated_audio.mp3"):
    """Convert translated text to speech and save it as an audio file."""
    try:
        myobj = gTTS(text=text_data, lang=to_language, slow=False)
        myobj.save(output_file)
        return output_file
    except Exception as e:
        st.error(f"Error in text-to-voice conversion: {e}")
        return None

def summarize_text_with_sumy(text, sentence_count=3):
    """Summarize the given text using sumy library's LSA summarization."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join([str(sentence) for sentence in summary])

def create_pdf(summary_text):
    """Create a PDF file from the summary text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)  # Allows for multi-line text
    pdf_file_path = "summary.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Load user credentials from JSON file
def load_user_credentials():
    if os.path.exists("user_credentials.json"):
        with open("user_credentials.json", "r") as f:
            return json.load(f)
    return {}

# Save user credentials to JSON file
def save_user_credentials(credentials):
    with open("user_credentials.json", "w") as f:
        json.dump(credentials, f)

# Load user data from JSON file
def load_user_data(username):
    if os.path.exists(f"{username}_data.json"):
        with open(f"{username}_data.json", "r") as f:
            return json.load(f)
    return []

# Save user data to JSON file
def save_user_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)

# Streamlit UI
if "username" not in st.session_state:
    st.session_state.username = None

# Load user credentials
user_credentials = load_user_credentials()

# Handle Login page
def login_page():
    st.title("User Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        # Validate user credentials
        if username in user_credentials and user_credentials[username]['password'] == password:
            st.session_state.username = username
            st.success("Login successful!")
            st.session_state.user_data = load_user_data(username)
            st.experimental_rerun
        else:
            st.error("Invalid credentials.")
    
    if st.button("Create New Account"):
        st.session_state.create_account = True
        st.experimental_rerun()  # Rerun to switch to create account page

# Handle Create Account page
def create_account_page():
    st.title("Create New Account")
    name = st.text_input("Full Name", key="full_name")
    new_username = st.text_input("Username", key="new_username")
    new_password = st.text_input("Password", type="password", key="new_password")
    
    if st.button("Create Account"):
        if new_username in user_credentials:
            st.error("Username already exists. Choose a different username.")
        else:
            # Save new user credentials
            user_credentials[new_username] = {
                "name": name,
                "password": new_password
            }
            save_user_credentials(user_credentials)
            st.success("Account created successfully! You can now log in.")
            st.session_state.create_account = False  # Reset the session state
            st.experimental_rerun()  # Rerun to go back to login page

    if st.button("Back to Login"):
        st.session_state.create_account = False
        st.experimental_rerun()  # Rerun to switch back to login page

# Main application after login
def main_app():
    st.title(f"Welcome, {st.session_state.username}!")
      # Add a logout button
    if st.sidebar.button("Logout"):
        st.session_state.username = None  # Reset the username in session state
        st.session_state.user_data = None  # Reset user data
        st.experimental_rerun()  # Reload the app to go back to the login page
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Translate Audio", "Summarize Audio", "Past Activities"])

    if page == "Translate Audio":
        st.subheader("YouTrancribe - Audio Translation")

        # Input for the YouTube link
        video_url = st.text_input("Enter YouTube Video URL:", key="video_url")

        # Dropdown for selecting the target language
        to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()), key="to_language")
        to_language = get_language_code(to_language_name)

        # Button to trigger translation
        start_button = st.button("Start", key="translate_start")

        if start_button and video_url:
            st.write("Downloading audio...")
            audio_path = download_youtube_audio(video_url)
            if audio_path:
                st.write("Converting audio to WAV...")
                wav_path = convert_to_wav(audio_path)
                if wav_path:
                    st.write("Extracting text from audio...")
                    detected_text = extract_text_from_audio(wav_path)
                    if detected_text:
                        from_language = detect_language(detected_text)
                        st.write(f"Detected Language: {from_language}")
                        st.write(f"Translating to {to_language_name}...")
                        translated_text = translator_function(detected_text, from_language, to_language)
                        if translated_text:
                            st.write("Generating translated audio file...")
                            translated_audio_file = text_to_voice(translated_text, to_language)
                            if translated_audio_file and os.path.exists(translated_audio_file):
                                # Provide a download link for the translated audio file
                                with open(translated_audio_file, "rb") as audio_file:
                                    st.download_button(
                                        label="Download Translated Audio",
                                        data=audio_file,
                                        file_name="translated_audio.mp3",
                                        mime="audio/mp3"
                                    )

                                # Save the translation data
                                st.session_state.user_data.append({
                                    "video_url": video_url,
                                    "translated_text": translated_text
                                })
                                save_user_data(st.session_state.username, st.session_state.user_data)

                            # Clean up the translated audio file after download
                            if os.path.exists(translated_audio_file):
                                os.remove(translated_audio_file)

                        # Clean up the temporary WAV file
                        os.remove(wav_path)

                # Clean up the downloaded audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)

    elif page == "Summarize Audio":
        st.subheader("YouTrancribe - Audio Summarization")

        # Input for the YouTube link
        video_url = st.text_input("Enter YouTube Video URL for Summarization:", key="video_summarize_url")

        # Button to trigger summarization
        start_summarize_button = st.button("Summarize", key="summarize_start")

        if start_summarize_button and video_url:
            st.write("Downloading audio for summarization...")
            audio_path = download_youtube_audio(video_url)
            if audio_path:
                st.write("Converting audio to WAV...")
                wav_path = convert_to_wav(audio_path)
                if wav_path:
                    st.write("Extracting text from audio...")
                    detected_text = extract_text_from_audio(wav_path)
                    if detected_text:
                        st.write("Summarizing text...")
                        summary = summarize_text_with_sumy(detected_text)
                        st.write("Summary:")
                        st.write(summary)

                        # Create a PDF from the summary
                        pdf_file_path = create_pdf(summary)
                        st.write("Summary PDF created successfully!")

                        # Provide a download link for the PDF
                        with open(pdf_file_path, "rb") as pdf_file:
                            st.download_button(
                                label="Download Summary PDF",
                                data=pdf_file,
                                file_name="summary.pdf",
                                mime="application/pdf"
                            )

                        # Save the summarization data
                        st.session_state.user_data.append({
                            "video_url": video_url,
                            "summary": summary
                        })
                        save_user_data(st.session_state.username, st.session_state.user_data)

                    # Clean up the temporary WAV file
                    os.remove(wav_path)

                # Clean up the downloaded audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)

    elif page == "Past Activities":
        st.subheader("Your Past Activities")
        if st.session_state.user_data:
            for activity in st.session_state.user_data:
                st.write(f"Video URL: {activity.get('video_url')}")
                if 'translated_text' in activity:
                    st.write(f"Translated Text: {activity.get('translated_text')}")
                if 'summary' in activity:
                    st.write(f"Summary: {activity.get('summary')}")
        else:
            st.write("No past activities found.")

# Check which page to display
if st.session_state.username is None:
    if "create_account" in st.session_state and st.session_state.create_account:
        create_account_page()  # Show create account page
    else:
        login_page()  # Show login page
else:
    main_app()  # Show main application after login
