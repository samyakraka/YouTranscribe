def main_app():
    st.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Translate Audio", "Summarize Audio", "Past Activities"])

    if page == "Translate Audio":
        st.subheader("YouTube Audio Language Translator")

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
        st.subheader("Audio Summarization")

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
