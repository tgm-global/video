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
st.markdown("Images upload karein, unka **exact sequence** set karein, aur automatic voice speed sync ke sath **MP4 Video** banayein!")

# Session state to maintain exact selection order of images
if "ordered_images" not in st.session_state:
    st.session_state.ordered_images = []  # List of dicts: {"id": unique_key, "name": str, "bytes": bytes}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 1. Image Upload Section
st.subheader("1️⃣ Apni Images Upload Karein (Selection Order ke Sath)")
st.caption("💡 **Tip:** Agar aap ek-ek karke images select karenge, toh jis order mein aap select karenge (1st, 2nd, 3rd...), woh bilkul usi number par judti jayengi!")

uploaded_files = st.file_uploader(
    "Images chunein (Ek-ek karke ya ek sath multiple select karein):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

# Append newly selected images in the exact order they arrive
if uploaded_files:
    existing_ids = {item["id"] for item in st.session_state.ordered_images}
    added_new = False
    for f in uploaded_files:
        file_bytes = f.getvalue()
        unique_id = f"{f.name}_{len(file_bytes)}"
        if unique_id not in existing_ids:
            st.session_state.ordered_images.append({
                "id": unique_id,
                "name": f.name,
                "bytes": file_bytes
            })
            existing_ids.add(unique_id)
            added_new = True
    if added_new:
        # Reset uploader widget so user can easily add more images one-by-one in exact order
        st.session_state.uploader_key += 1
        st.rerun()

# Display & Reorder Selected Images
if st.session_state.ordered_images:
    col_info, col_clear = st.columns([3, 1])
    with col_info:
        st.success(f"✅ Kul {len(st.session_state.ordered_images)} images sequence mein set hain:")
    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.ordered_images = []
            st.session_state.uploader_key += 1
            st.rerun()

    # Show images in grid with Move Left/Right & Remove controls
    num_imgs = len(st.session_state.ordered_images)
    cols = st.columns(min(num_imgs, 4))
    
    for idx, img_data in enumerate(st.session_state.ordered_images):
        with cols[idx % 4]:
            st.markdown(f"**Slide #{idx + 1}**")
            st.image(img_data["bytes"], caption=img_data["name"][:18], use_container_width=True)
            
            b1, b2, b3 = st.columns(3)
            with b1:
                if idx > 0 and st.button("⬅️", key=f"left_{idx}", help="Pehle laayein"):
                    st.session_state.ordered_images[idx], st.session_state.ordered_images[idx - 1] = (
                        st.session_state.ordered_images[idx - 1],
                        st.session_state.ordered_images[idx],
                    )
                    st.rerun()
            with b2:
                if idx < num_imgs - 1 and st.button("➡️", key=f"right_{idx}", help="Baad mein bhejein"):
                    st.session_state.ordered_images[idx], st.session_state.ordered_images[idx + 1] = (
                        st.session_state.ordered_images[idx + 1],
                        st.session_state.ordered_images[idx],
                    )
                    st.rerun()
            with b3:
                if st.button("❌", key=f"del_{idx}", help="Hatayein"):
                    st.session_state.ordered_images.pop(idx)
                    st.rerun()

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
    if not st.session_state.ordered_images:
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
            asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path, rate_str="+0%"))
            
            if duration_choice != "Auto (Script ke hisaab se)":
                if duration_choice == "Custom Seconds":
                    target_duration = float(custom_seconds)
                else:
                    target_duration = float(duration_choice.split(" ")[0])

                base_clip = AudioFileClip(temp_audio_path)
                base_duration = base_clip.duration
                base_clip.close()

                speed_ratio = base_duration / target_duration
                rate_percent = int(round((speed_ratio - 1.0) * 100))
                rate_percent = max(-40, min(80, rate_percent))
                rate_str = f"{rate_percent:+d}%"

                progress_text.text(f"⚡ Voice speed ko {target_duration:.0f}s video ke mutabiq ({rate_str}) adjust kiya ja raha hai...")
                asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path, rate_str=rate_str))
            else:
                target_duration = None

            # Step 2: Process Ordered Images to Selected Resolution
            progress_text.text("🖼️ Step 2/3: Images ko exact Slide #1, #2, #3... sequence mein set kiya ja raha hai...")
            
            if "1080x1920" in video_format:
                target_size = (1080, 1920)
            elif "1080x1080" in video_format:
                target_size = (1080, 1080)
            else:
                target_size = (1920, 1080)

            from io import BytesIO
            for img_data in st.session_state.ordered_images:
                img = Image.open(BytesIO(img_data["bytes"])).convert("RGB")
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    img.save(tmp_img.name, format="JPEG", quality=95)
                    temp_image_paths.append(tmp_img.name)

            # Step 3: Merge Images & Audio into Final MP4 Video
            progress_text.text("🎬 Step 3/3: Images aur Voiceover ko jod kar MP4 video ban rahi hai...")
            
            audio_clip = AudioFileClip(temp_audio_path)
            final_duration = target_duration if target_duration is not None else audio_clip.duration
            duration_per_image = final_duration / len(temp_image_paths)
            
            clips = [ImageClip(img_path).set_duration(duration_per_image) for img_path in temp_image_paths]
            final_video = concatenate_videoclips(clips, method="compose")
            
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
