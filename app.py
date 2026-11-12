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
st.markdown("Images upload karein, video ka **Time Frame** chunein, aur automatic voice speed sync ke sath **MP4 Video** banayein!")

# 1. Image Upload Section
st.subheader("1️⃣ Apni Images Upload Karein")
uploaded_files = st.file_uploader(
    "Multiple images select karein (JPG, JPEG, PNG):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} images select ki gayi hain. Video mein yeh isi sequence mein dikhengi.")
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(file, caption=f"Slide {idx+1}", use_container_width=True)

st.markdown("---")

# 2. Text-to-Voice & Time Frame Section
st.subheader("2️⃣ Voiceover Script, Voice & Time Frame")

voice_text = st.text_area(
    "Voiceover Script (Jo video mein bolna hai):",
    value="Kya aapka business abhi tak online nahi hai? Aaj hi banwayein ek professional website, woh bhi sirf nau sau ninaanve rupaye mein! Contact karein Delhi NCR Web Design.",
    height=110
)

col1, col2, col3 = st.columns(3)
with col1:
    voice_option = st.selectbox(
        "Select Natural Voice:", 
        [
            "Swara (Hindi - Female)", 
            "Madhur (Hindi - Male)", 
            "Aria (English - Female)", 
            "Guy (English - Male)"
        ]
    )
with col2:
    video_format = st.selectbox(
        "Video Format:",
        [
            "Reels / Shorts (1080x1920)",
            "Instagram Post (1080x1080)",
            "YouTube (1920x1080)"
        ]
    )
with col3:
    duration_choice = st.selectbox(
        "Video Time Frame:",
        [
            "Auto (Script ke hisaab se)",
            "10 Seconds",
            "15 Seconds",
            "20 Seconds",
            "30 Seconds",
            "45 Seconds",
            "60 Seconds",
            "Custom Seconds"
        ]
    )

custom_seconds = 15
if duration_choice == "Custom Seconds":
    custom_seconds = st.number_input("Apna Custom Time Frame dalein (Seconds mein):", min_value=5, max_value=300, value=25, step=1)

generate_btn = st.button("🚀 Generate Instant MP4 Video", type="primary", use_container_width=True)

# Async function for Edge-TTS with dynamic rate
async def generate_natural_audio(text, voice_name, output_file, rate_str="+0%"):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate_str, pitch="+0Hz")
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
            voice_mapping = {
                "Swara (Hindi - Female)": "hi-IN-SwaraNeural",
                "Madhur (Hindi - Male)": "hi-IN-MadhurNeural",
                "Aria (English - Female)": "en-US-AriaNeural",
                "Guy (English - Male)": "en-US-GuyNeural",
            }
            selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                temp_audio_path = tmp_audio.name

            # Step 1: Generate Voiceover with Auto-Speed Sync according to Time Frame
            progress_text.text("🎙️ Step 1/3: Voiceover aur speed sync calculate ho raha hai...")
            
            # Pehle normal (+0%) speed par audio bana kar base duration check karein
            asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path, rate_str="+0%"))
            
            if duration_choice != "Auto (Script ke hisaab se)":
                if duration_choice == "Custom Seconds":
                    target_duration = float(custom_seconds)
                else:
                    target_duration = float(duration_choice.split(" ")[0])

                base_clip = AudioFileClip(temp_audio_path)
                base_duration = base_clip.duration
                base_clip.close()

                # Calculate required speed percentage to fit target_duration
                # Example: agar script 15s ki hai aur video 10s ki banani hai, toh speed +50% hogi
                speed_ratio = base_duration / target_duration
                rate_percent = int(round((speed_ratio - 1.0) * 100))
                
                # Clamp rate between -40% and +80% taaki voice natural aur samajh aane layak rahe
                rate_percent = max(-40, min(80, rate_percent))
                rate_str = f"{rate_percent:+d}%"

                progress_text.text(f"⚡ Voice speed ko {target_duration:.0f}s video ke mutabiq ({rate_str}) adjust kiya ja raha hai...")
                asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path, rate_str=rate_str))
            else:
                target_duration = None

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
            
            # Final video duration set karein
            final_duration = target_duration if target_duration is not None else audio_clip.duration
            duration_per_image = final_duration / len(temp_image_paths)
            
            clips = [ImageClip(img_path).set_duration(duration_per_image) for img_path in temp_image_paths]
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Agar audio thoda sa lamba/chota bacha ho toh video duration ke exact trim/fit karein
            if audio_clip.duration > final_duration:
                audio_clip = audio_clip.subclip(0, final_duration)
            
            final_video = final_video.set_audio(audio_clip).set_duration(final_duration)
            
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
            
            progress_text.text(f"✅ Aapki {final_duration:.1f} Seconds ki Video Tayar Hai!")
            st.success(f"🎉 Video ({final_duration:.1f} sec) successfully ban gayi hai! Neeche preview dekhein aur download karein.")
            
            st.video(final_video_path)
            
            with open(final_video_path, "rb") as vid_file:
                video_bytes = vid_file.read()
            
            st.download_button(
                label=f"📥 Download {int(final_duration)}s Video (.mp4)",
                data=video_bytes,
                file_name=f"delhi_ncr_promo_{int(final_duration)}s.mp4",
                mime="video/mp4"
            )

        except Exception as e:
            st.error(f"Video banane mein error aaya: {e}")
