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
    font_size = st.slider("Text Size", 20, 80, 40)

# Helper function to generate text frame using PIL (Bypasses ImageMagick)
def create_text_image(text, size, font_size, text_color_hex, bg_color_hex):
    width, height = size
    
    # Create image with background color
    img = Image.new("RGB", (width, height), bg_color_hex)
    draw = ImageDraw.Draw(img)
    
    # Load font (fallback gracefully if custom font isn't found)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # Word wrapping helper
    margin = 100
    max_width = width - (2 * margin)
    
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        # Use textbbox for text sizing
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    wrapped_text = "\n".join(lines)
    
    # Draw centered text
    draw.multiline_text(
        (width / 2, height / 2),
        wrapped_text,
        fill=text_color_hex,
        font=font,
        anchor="mm",
        align="center"
    )
    
    return np.array(img)

# Generate Button
if st.button("🚀 Generate Video"):
    if not script_text.strip():
        st.error("Please enter a script first!")
    else:
        with st.spinner("1/3 Generating voiceover audio..."):
            os.makedirs("output", exist_ok=True)
            audio_path = "output/temp_audio.mp3"
            
            # Generate Audio via gTTS
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(audio_path)
            
            audio_clip = AudioFileClip(audio_path)
            video_duration = audio_clip.duration

        with st.spinner("2/3 Synthesizing animated frames..."):
            width, height = 1920, 1080
            
            # Clean sentences into subtitle chunks
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', script_text) if s.strip()]
            chunk_duration = video_duration / max(len(sentences), 1)

            video_clips = []
            for i, sentence in enumerate(sentences):
                # Create PIL image frame for this sentence
                frame_np = create_text_image(
                    text=sentence,
                    size=(width, height),
                    font_size=font_size,
                    text_color_hex=text_color,
                    bg_color_hex=bg_color
                )
                
                # Convert frame to MoviePy ImageClip
                img_clip = (
                    ImageClip(frame_np)
                    .set_start(i * chunk_duration)
                    .set_duration(chunk_duration)
                )
                video_clips.append(img_clip)

        with st.spinner("3/3 Rendering final video..."):
            # Composite Video + Audio
            final_clip = CompositeVideoClip(video_clips).set_audio(audio_clip)
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
