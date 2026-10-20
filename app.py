import os
import re
import streamlit as st
from gtts import gTTS
from moviepy.editor import (
    TextClip,
    AudioFileClip,
    CompositeVideoClip,
    ColorClip,
)

# Page Configuration
st.set_page_config(page_title="Custom YouTube Video Generator", layout="centered")
st.title("🎬 Free YouTube Video Generator")
st.write("Generate custom videos programmatically without any generation limits!")

# Inputs
video_title = st.text_input("Project Name", "My_First_Video")
script_text = st.text_area(
    "Enter Video Script / Voiceover Text",
    "Welcome back to the channel! Today we are building our own video creation app using Python.",
    height=150,
)

# Customization Options
col1, col2, col3 = st.columns(3)
with col1:
    bg_color = st.color_picker("Background Color", "#101820")
with col2:
    text_color = st.color_picker("Text Color", "#F2AA4C")
with col3:
    font_size = st.slider("Text Size", 30, 80, 50)

# Generate Button
if st.button("🚀 Generate Video"):
    if not script_text.strip():
        st.error("Please enter a script first!")
    else:
        with st.spinner("1/3 Generating voiceover audio..."):
            os.makedirs("output", exist_ok=True)
            audio_path = "output/temp_audio.mp3"
            
            # Generate Audio via gTTS (Free Google Text-to-Speech)
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(audio_path)
            
            audio_clip = AudioFileClip(audio_path)
            video_duration = audio_clip.duration

        with st.spinner("2/3 Synthesizing animated elements & background..."):
            # Create Background Clip (1080x1920 for Shorts or 1920x1080 for Widescreen)
            # Standard Widescreen YouTube resolution: (1920, 1080)
            width, height = 1920, 1080
            bg_clip = ColorClip(size=(width, height), color=tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), duration=video_duration)

            # Clean sentences into subtitle chunks
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script_text) if s.strip()]
            chunk_duration = video_duration / max(len(sentences), 1)

            text_clips = []
            for i, sentence in enumerate(sentences):
                # Create animated text overlay per sentence
                txt_clip = (
                    TextClip(
                        sentence,
                        fontsize=font_size,
                        color=text_color,
                        font="Arial",
                        size=(width - 200, None),
                        method="caption"
                    )
                    .set_position("center")
                    .set_start(i * chunk_duration)
                    .set_duration(chunk_duration)
                )
                text_clips.append(txt_clip)

        with st.spinner("3/3 Rendering final video on CPU..."):
            # Composite Video + Audio
            final_clip = CompositeVideoClip([bg_clip] + text_clips)
            final_clip = final_clip.set_audio(audio_clip)

            output_file = f"output/{video_title}.mp4"
            
            # Render video via CPU using FFmpeg
            final_clip.write_videofile(
                output_file,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

        st.success("🎉 Video rendered successfully!")
        
        # Download Button
        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Download YouTube Video (.mp4)",
                data=file,
                file_name=f"{video_title}.mp4",
                mime="video/mp4"
            )