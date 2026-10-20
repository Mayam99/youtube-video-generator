import os
import re
import numpy as np
import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
)

# Page Configuration
st.set_page_config(page_title="Cartoon & Educational Video Generator", layout="centered")
st.title("🎨 Kids & Adult Cartoon Creator")
st.write("Generate educational and fun animated videos seamlessly from your phone or PC!")

# Video Format & Purpose Selection
format_choice = st.selectbox(
    "Choose Video Format", 
    ["YouTube Shorts / Phone Vertical (9:16)", "YouTube Widescreen (16:9)"]
)

if "9:16" in format_choice:
    width, height = 1080, 1920
else:
    width, height = 1920, 1080

# Preset Themes for Kids vs Adults
theme = st.selectbox(
    "Choose Theme Style", 
    ["Bright Kids Fun (Bright Blue & Yellow)", "Educational Dark (Slate & Gold)", "Custom Colors"]
)

if theme == "Bright Kids Fun (Bright Blue & Yellow)":
    bg_color, text_color = "#1E90FF", "#FFFF00"
elif theme == "Educational Dark (Slate & Gold)":
    bg_color, text_color = "#101820", "#F2AA4C"
else:
    col_a, col_b = st.columns(2)
    with col_a:
        bg_color = st.color_picker("Background Color", "#101820")
    with col_b:
        text_color = st.color_picker("Text Color", "#F2AA4C")

font_size = st.slider("Text Size", 20, 100, 50)

# Inputs
video_title = st.text_input("Project Name", "Cartoon_Story_1")
script_text = st.text_area(
    "Enter Script / Educational Story",
    "Welcome little learners! Today we are exploring numbers and counting from one to five.",
    height=150,
)

# Helper function to generate text frame using PIL
def create_text_image(text, size, font_size, text_color_hex, bg_color_hex):
    w_img, h_img = size
    img = Image.new("RGB", (w_img, h_img), bg_color_hex)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    margin = 80
    max_w = w_img - (2 * margin)
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w_text = bbox[2] - bbox[0]
        if w_text <= max_w:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    wrapped_text = "\n".join(lines)
    
    draw.multiline_text(
        (w_img / 2, h_img / 2),
        wrapped_text,
        fill=text_color_hex,
        font=font,
        anchor="mm",
        align="center"
    )
    
    return np.array(img)

# Generate Button
if st.button("🚀 Generate Cartoon Video"):
    if not script_text.strip():
        st.error("Please enter a script first!")
    else:
        with st.spinner("1/3 Generating voiceover audio..."):
            os.makedirs("output", exist_ok=True)
            audio_path = "output/temp_audio.mp3"
            
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(audio_path)
            
            audio_clip = AudioFileClip(audio_path)
            video_duration = audio_clip.duration

        with st.spinner("2/3 Synthesizing animated frames..."):
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script_text) if s.strip()]
            chunk_duration = video_duration / max(len(sentences), 1)

            video_clips = []
            for i, sentence in enumerate(sentences):
                frame_np = create_text_image(
                    text=sentence,
                    size=(width, height),
                    font_size=font_size,
                    text_color_hex=text_color,
                    bg_color_hex=bg_color
                )
                
                img_clip = (
                    ImageClip(frame_np)
                    .set_start(i * chunk_duration)
                    .set_duration(chunk_duration)
                )
                video_clips.append(img_clip)

        with st.spinner("3/3 Rendering final video..."):
            final_clip = CompositeVideoClip(video_clips).set_audio(audio_clip)
            output_file = f"output/{video_title}.mp4"
            
            final_clip.write_videofile(
                output_file,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

        st.success("🎉 Cartoon video rendered successfully!")
        
        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Download Video (.mp4)",
                data=file,
                file_name=f"{video_title}.mp4",
                mime="video/mp4"
            )
