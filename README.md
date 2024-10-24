
## YouTranscribe

**YouTranscribe** is a powerful tool that allows users to transcribe, translate, and summarize audio content from YouTube videos seamlessly. With an intuitive user interface built on Streamlit, this application harnesses the capabilities of various libraries to enhance the accessibility and understanding of video content in different languages.

### Features

- **YouTube Audio Extraction**: Download audio from any YouTube video URL.
- **Speech Recognition**: Convert spoken content from audio to text using advanced speech recognition technology.
- **Language Detection**: Automatically detect the language of the spoken content.
- **Translation**: Translate transcribed text into a variety of languages using Google Translate API.
- **Audio to Speech Conversion**: Generate translated audio files for easy listening.
- **Summarization**: Summarize transcribed text using natural language processing techniques to provide concise overviews of video content.
- **User Accounts**: Create and manage user accounts, allowing for personalized data storage and access to past activities.

### Tech Stack

- **Frontend**: Streamlit for the user interface.
- **Backend**: Python with libraries including yt-dlp, SpeechRecognition, gTTS, and sumy.
- **Data Storage**: JSON files for user data management.

### Getting Started

To run the application locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/samyakraka2908/YouTranscribe.git
   cd YouTranscribe
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

### Contributions

Contributions are welcome! Please feel free to open issues or submit pull requests to improve the functionality of YouTranscribe.

### License

This project is licensed under the MIT License.

---
