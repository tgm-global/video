import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(
    page_title="TGM Fast Video Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Promo Video Studio")
st.markdown("Apni promotional images upload karein, voiceover script likhein, aur instant **MP4 Video** banayein!")

# 1. Image Upload Section
st.subheader("1️⃣ Apni Images Upload Karein")
uploaded_files = st.file_uploader(
    "Multiple images select karein (JPG, JPEG, PNG):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} images select ki gayi hain. Video mein yeh isi sequence mein dikhengi.")
    # Preview uploaded images in small columns
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(file, caption=f"Slide {idx+1}", use_container_width=True)

st.markdown("---")

# 2. Text-to-Voice Section
st.subheader("2️⃣ Voiceover Script & Voice Selection")

voice_text = st.text_area(
    "Voiceover Script (Jo video mein bolna hai):",
    value="Kya aapka business abhi tak online nahi hai? Aaj hi banwayein ek professional website, woh bhi sirf nau sau ninaanve rupaye mein! Contact karein Delhi NCR Web Design.",
    height=110
)

col1, col2 = st.columns(2)
with col1:
    voice_option = st.selectbox(
        "Select Natural Voice:", 
        [
            "Swara (Hindi - Female, Natural & Warm)", 
            "Madhur (Hindi - Male, Deep & Professional)", 
            "Aria (English - Female, Professional)", 
            "Guy (English - Male, Conversational)"
        ]
    )
with col2:
    video_format = st.selectbox(
        "Video Format (Resolution):",
        [
            "Vertical / Reels (1080x1920)",
            "Square / Instagram Post (1080x1080)",
            "Landscape / YouTube (1920x1080)"
        ]
    )

generate_btn = st.button("🚀 Generate Instant MP4 Video", type="primary", use_container_width=True)

# Async function for natural Edge-TTS voice
async def generate_natural_audio(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name, rate="+0%", pitch="+0Hz")
    await communicate.save(output_file)

if generate_btn:
    if not uploaded_files:
        st.warning("Kripya pehle kam se kam ek image upload karein!")
    elif not voice_text.strip():
        st.warning("Kripya voiceover script zaroor likhein!")
    else:
        progress_text = st.empty()
        temp_image_paths = []
        
        try:
            # Step 1: Generate Voiceover Audio
            progress_text.text("🎙️ Step 1/3: Realistic voiceover generate ho raha hai...")
            voice_mapping = {
                "Swara (Hindi - Female, Natural & Warm)": "hi-IN-SwaraNeural",
                "Madhur (Hindi - Male, Deep & Professional)": "hi-IN-MadhurNeural",
                "Aria (English - Female, Professional)": "en-US-AriaNeural",
                "Guy (English - Male, Conversational)": "en-US-GuyNeural",
            }
            selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                temp_audio_path = tmp_audio.name

            asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path))

            # Step 2: Process Uploaded Images to Selected Resolution
            progress_text.text("🖼️ Step 2/3: Images ko video size mein set kiya ja raha hai...")
            
            if "1080x1920" in video_format:
                target_size = (1080, 1920)
            elif "1080x1080" in video_format:
                target_size = (1080, 1080)
            else:
                target_size = (1920, 1080)

            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file).convert("RGB")
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    img.save(tmp_img.name, format="JPEG", quality=95)
                    temp_image_paths.append(tmp_img.name)

            # Step 3: Merge Images & Audio into Final MP4 Video
            progress_text.text("🎬 Step 3/3: Images aur Voiceover ko jod kar MP4 video ban rahi hai...")
            
            audio_clip = AudioFileClip(temp_audio_path)
            total_duration = audio_clip.duration
            duration_per_image = total_duration / len(temp_image_paths)
            
            clips = [ImageClip(img_path).set_duration(duration_per_image) for img_path in temp_image_paths]
            final_video = concatenate_videoclips(clips, method="compose")
            final_video = final_video.set_audio(audio_clip)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                final_video_path = tmp_vid.name
            
            final_video.write_videofile(
                final_video_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                logger=None
            )
            
            audio_clip.close()
            final_video.close()
            
            progress_text.text("✅ Aapki Promotional Video Tayar Hai!")
            st.success("🎉 Video successfully ban gayi hai! Neeche preview dekhein aur download karein.")
            
            # Display Video & Download Button
            st.video(final_video_path)
            
            with open(final_video_path, "rb") as vid_file:
                video_bytes = vid_file.read()
            
            st.download_button(
                label="📥 Download Final Video (.mp4)",
                data=video_bytes,
                file_name="delhi_ncr_web_design_promo.mp4",
                mime="video/mp4"
            )

        except Exception as e:
            st.error(f"Video banane mein error aaya: {e}")
