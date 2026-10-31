import os
import re
import math
import numpy as np
import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    CompositeAudioClip,
)
from moviepy.audio.fx.all import audio_loop

# Page Configuration
st.set_page_config(page_title="Cartoon & Educational Video Generator", layout="centered")
st.title("🎨 Kids & Adult Cartoon Creator")
st.write("Upgraded with Programmatic Cartoon Graphics & Dynamic Shapes!")

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
    ["Bright Kids Fun (Multi-Color Cycling)", "Educational Dark (Slate & Gold)", "Custom Colors"]
)

CARTOON_PALETTE = ["#1E90FF", "#FFD700", "#32CD32", "#FF69B4", "#9370DB", "#FFA500", "#00CED1"]

if theme == "Bright Kids Fun (Multi-Color Cycling)":
    text_color, accent_color = "#FFFFFF", "#101820"
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

# Optional Background Music Upload
st.subheader("🎵 Audio Settings")
bg_music_file = st.file_uploader("Upload Background Music (Optional MP3/WAV)", type=["mp3", "wav"])
bg_music_volume = st.slider("Background Music Volume", 0.0, 1.0, 0.1)

# Inputs
video_title = st.text_input("Project Name", "Cartoon_Story_Graphics")
script_text = st.text_area(
    "Enter Script / Educational Story",
    "Welcome little learners! Today we are exploring numbers, counting stars, discovering cute animals, reading books, and learning bright colors together!",
    height=150,
)

# Helper function to draw a custom cartoon star graphic
def draw_cartoon_star(draw, center, radius, color):
    cx, cy = center
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.4
        angle = i * math.pi / 5 - math.pi / 2
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color)

# Helper function to draw a custom cartoon shape icon based on text keywords
def draw_cartoon_graphic(draw, text, center, accent_hex):
    cx, cy = center
    text_lower = text.lower()
    
    if any(k in text_lower for k in ["star", "shine", "bright"]):
        # Draw a cluster of cartoon stars
        draw_cartoon_star(draw, (cx, cy), 65, "#FFD700")
        draw_cartoon_star(draw, (cx - 90, cy - 20), 40, "#FFFFFF")
        draw_cartoon_star(draw, (cx + 90, cy - 20), 40, "#FFFFFF")
    elif any(k in text_lower for k in ["number", "count", "one", "two", "three"]):
        # Draw a bouncy counting badge circle
        draw.ellipse([cx - 75, cy - 75, cx + 75, cy + 75], fill="#FFFFFF", outline=accent_hex, width=8)
        # We can also draw inner concentric rings
        draw.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], outline="#FF4500", width=6)
    elif any(k in text_lower for k in ["animal", "dog", "cat", "pet"]):
        # Draw cute animal paw / heart shapes
        draw.ellipse([cx - 50, cy - 30, cx - 10, cy + 10], fill="#FFFFFF")
        draw.ellipse([cx + 10, cy - 30, cx + 50, cy + 10], fill="#FFFFFF")
        draw.ellipse([cx - 30, cy - 60, cx + 30, cy - 10], fill="#FFFFFF")
        draw.ellipse([cx - 25, cy + 10, cx + 25, cy + 50], fill="#FFFFFF")
    else:
        # Default bouncy cartoon educational shapes (overlapping colorful circles)
        draw.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill="#FFFFFF", outline=accent_hex, width=6)
        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=accent_hex)

# Helper function to generate frames with borders, clean banners, and custom graphics
def create_text_image(text, size, font_size, text_color_hex, bg_color_hex, accent_color_hex, video_title_text):
    w_img, h_img = size
    img = Image.new("RGB", (w_img, h_img), bg_color_hex)
    draw = ImageDraw.Draw(img)
    
    border_width = 30
    draw.rectangle(
        [border_width, border_width, w_img - border_width, h_img - border_width],
        outline=accent_color_hex,
        width=12
    )
    
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

    # Draw clean header title
    draw.text(
        (w_img / 2, border_width + (banner_height / 2)),
        video_title_text.upper(),
        fill="#FFFFFF",
        font=header_font,
        anchor="mm",
        align="center"
    )

    # Calculate center position for cartoon graphics and text
    body_top = border_width + banner_height
    body_center_y = body_top + ((h_img - body_top - border_width) / 2)
    
    # Draw custom cartoon graphic sticker above text
    graphic_y = body_center_y - int(font_size * 2.5)
    draw_cartoon_graphic(draw, text, (w_img / 2, graphic_y), accent_color_hex)

    # Word wrapping for main text
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
    
    text_y = body_center_y + int(font_size * 0.6)
    draw.multiline_text(
        (w_img / 2, text_y),
        wrapped_text,
        fill=text_color_hex,
        font=font,
        anchor="mm",
        align="center"
    )
    
    return np.array(img)

# Generate Button
if st.button("🚀 Generate Cartoon Graphic Video"):
    if not script_text.strip():
        st.error("Please enter a script first!")
    else:
        with st.spinner("1/3 Generating voiceover and audio tracks..."):
            os.makedirs("output", exist_ok=True)
            audio_path = "output/temp_audio.mp3"
            
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(audio_path)
            
            voice_clip = AudioFileClip(audio_path)
            video_duration = voice_clip.duration

            if bg_music_file is not None:
                bg_music_path = "output/temp_bgm.mp3"
                with open(bg_music_path, "wb") as f:
                    f.write(bg_music_file.getbuffer())
                
                bg_clip = AudioFileClip(bg_music_path)
                if bg_clip.duration < video_duration:
                    bg_clip = audio_loop(bg_clip, duration=video_duration)
                else:
                    bg_clip = bg_clip.subclip(0, video_duration)
                
                bg_clip = bg_clip.volumex(bg_music_volume)
                final_audio = CompositeAudioClip([voice_clip, bg_clip])
            else:
                final_audio = voice_clip

        with st.spinner("2/3 Synthesizing frames with custom cartoon shapes and animations..."):
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script_text) if s.strip()]
            
            total_words = sum(len(s.split()) for s in sentences)
            if total_words == 0:
                total_words = 1

            video_clips = []
            current_time = 0.0
            
            for i, sentence in enumerate(sentences):
                sentence_words = len(sentence.split())
                chunk_duration = (sentence_words / total_words) * video_duration
                if chunk_duration < 0.6:
                    chunk_duration = 0.6

                if theme == "Bright Kids Fun (Multi-Color Cycling)":
                    current_bg = CARTOON_PALETTE[i % len(CARTOON_PALETTE)]
                else:
                    current_bg = bg_color

                frame_np = create_text_image(
                    text=sentence,
                    size=(width, height),
                    font_size=font_size,
                    text_color_hex=text_color,
                    bg_color_hex=current_bg,
                    accent_color_hex=accent_color,
                    video_title_text=video_title
                )
                
                img_clip = (
                    ImageClip(frame_np)
                    .set_start(current_time)
                    .set_duration(chunk_duration)
                )
                video_clips.append(img_clip)
                current_time += chunk_duration

        with st.spinner("3/3 Rendering final cartoon video..."):
            final_clip = CompositeVideoClip(video_clips).set_audio(final_audio)
            output_file = f"output/{video_title}.mp4"
            
            final_clip.write_videofile(
                output_file,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

        st.success("🎉 Cartoon graphic video rendered successfully!")
        
        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Download Video (.mp4)",
                data=file,
                file_name=f"{video_title}.mp4",
                mime="video/mp4"
            )
