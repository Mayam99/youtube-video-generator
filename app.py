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
st.write("Step 2: Enhanced with visual border frames, title banners, and cartoon styling!")

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
    bg_color, text_color, accent_color = "#1E90FF", "#FFFF00", "#FF4500"
elif theme == "Educational Dark (Slate & Gold)":
    bg_color, text_color, accent_color = "#101820", "#F2AA4C", "#4EA8DE"
else:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        bg_color = st.color_picker("Background Color", "#101820")
    with col_b:
        text_color = st.color_picker("Text Color", "#F2AA4C")
    with col_c:
        accent_color = st.color_picker("Accent Color", "#FF4500")

font_size = st.slider("Text Size", 20, 100, 50)

# Inputs
video_title = st.text_input("Project Name", "Cartoon_Story_Step2")
script_text = st.text_area(
    "Enter Script / Educational Story",
    "Welcome little learners! Today we are exploring fun shapes, colors, and counting numbers from one to five.",
    height=150,
)

# Helper function to generate enhanced visual frames with borders and banners
def create_text_image(text, size, font_size, text_color_hex, bg_color_hex, accent_color_hex, video_title_text):
    w_img, h_img = size
    img = Image.new("RGB", (w_img, h_img), bg_color_hex)
    draw = ImageDraw.Draw(img)
    
    # 1. Draw a cute decorative border frame
    border_width = 30
    draw.rectangle(
        [border_width, border_width, w_img - border_width, h_img - border_width],
        outline=accent_color_hex,
        width=12
    )
    
    # 2. Draw a top header banner for educational/cartoon style
    banner_height = int(h_img * 0.10)
    draw.rectangle(
        [border_width, border_width, w_img - border_width, border_width + banner_height],
        fill=accent_color_hex
    )
    
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        header_font = ImageFont.truetype("DejaVuSans.ttf", int(font_size * 0.65))
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
            header_font = ImageFont.truetype("Arial.ttf", int(font_size * 0.65))
        except:
            font = ImageFont.load_default()
            header_font = ImageFont.load_default()

    # Draw header title text inside the banner
    draw.text(
        (w_img / 2, border_width + (banner_height / 2)),
        "📚 " + video_title_text.upper(),
        fill="#FFFFFF",
        font=header_font,
        anchor="mm",
        align="center"
    )

    # 3. Word wrapping helper for main text content
    margin = 120
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
    
    # 4. Draw centered main text in the body area below the banner
    body_top = border_width + banner_height
    body_center_y = body_top + ((h_img - body_top - border_width) / 2)
    
    draw.multiline_text(
        (w_img / 2, body_center_y),
        wrapped_text,
        fill=text_color_hex,
        font=font,
        anchor="mm",
        align="center"
    )
    
    return np.array(img)

# Generate Button
if st.button("🚀 Generate Step 2 Video"):
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

        with st.spinner("2/3 Synthesizing animated frames with borders and banners..."):
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script_text) if s.strip()]
            chunk_duration = video_duration / max(len(sentences), 1)

            video_clips = []
            for i, sentence in enumerate(sentences):
                frame_np = create_text_image(
                    text=sentence,
                    size=(width, height),
                    font_size=font_size,
                    text_color_hex=text_color,
                    bg_color_hex=bg_color,
                    accent_color_hex=accent_color,
                    video_title_text=video_title
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

        st.success("🎉 Enhanced cartoon video rendered successfully!")
        
        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Download Video (.mp4)",
                data=file,
                file_name=f"{video_title}.mp4",
                mime="video/mp4"
            )
