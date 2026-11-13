import streamlit as st
import asyncio
import edge_tts
import tempfile
from io import BytesIO

# Page configuration (Centered layout works best on both Mobile & Desktop)
st.set_page_config(
    page_title="TGM Fast Video Studio",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Mobile-Responsive CSS
st.markdown("""
    <style>
    /* Mobile screen padding & touch optimization */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 720px;
    }
    /* Make buttons bigger and easier to tap on mobile */
    .stButton > button {
        min-height: 46px;
        font-size: 16px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    /* Optimize text areas & inputs for mobile touch */
    textarea, input, select {
        font-size: 16px !important;
    }
    /* Slide card styling */
    .slide-card {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 TGM Promo Video Studio")
st.caption("Mobile & Desktop Ready • Fast MP4 Video Generator")

# Initialize Session State
if "ordered_images" not in st.session_state:
    st.session_state.ordered_images = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 1. Image Upload Section
st.subheader("1️⃣ Apni Images Upload Karein")

uploaded_files = st.file_uploader(
    "Gallery se images chunein (JPG, JPEG, PNG):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

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
        st.session_state.uploader_key += 1
        st.rerun()

# 2. Mobile-Friendly Sequence Manager
if st.session_state.ordered_images:
    st.success(f"✅ Kul {len(st.session_state.ordered_images)} images selected hain.")
    
    if st.button("🗑️ Saari Images Hatayein (Clear All)", use_container_width=True):
        st.session_state.ordered_images = []
        st.session_state.uploader_key += 1
        st.rerun()

    num_imgs = len(st.session_state.ordered_images)
    
    # Clean Mobile-Friendly List View (No nested columns that freeze mobile browsers)
    for idx, img_data in enumerate(st.session_state.ordered_images):
        with st.container():
            st.markdown(f"**🖼️ Slide #{idx + 1}** — `{img_data['name'][:25]}`")
            
            # Preview thumbnail with fixed mobile-safe width
            st.image(img_data["bytes"], width=220)
            
            # Position selector + Delete button on clean row
            c1, c2 = st.columns([2, 1])
            with c1:
                position_options = [f"Position #{p}" for p in range(1, num_imgs + 1)]
                selected_pos_label = st.selectbox(
                    f"Slide {idx+1} Position:",
                    options=position_options,
                    index=idx,
                    key=f"pos_select_{img_data['id']}_{idx}",
                    label_visibility="collapsed"
                )
                new_pos = int(selected_pos_label.split("#")[1])
                if new_pos != idx + 1:
                    moved_item = st.session_state.ordered_images.pop(idx)
                    st.session_state.ordered_images.insert(new_pos - 1, moved_item)
                    st.rerun()
            with c2:
                if st.button("❌ Remove", key=f"del_{idx}", use_container_width=True):
                    st.session_state.ordered_images.pop(idx)
                    st.rerun()
            st.divider()

# 3. Text-to-Voice & Time Frame Section
st.subheader("2️⃣ Voiceover Script & Video Settings")

voice_text = st.text_area(
    "Voiceover Script (Jo video mein bolna hai):",
    value="Kya aapka business abhi tak online nahi hai? Aaj hi banwayein ek professional website, woh bhi sirf nau sau ninaanve rupaye mein! Contact karein Delhi NCR Web Design.",
    height=120
)

voice_option = st.selectbox(
    "Select Natural Voice:", 
    [
        "Swara (Hindi - Female)", 
        "Madhur (Hindi - Male)", 
        "Aria (English - Female)", 
        "Guy (English - Male)"
    ]
)

video_format = st.selectbox(
    "Video Format (Size):",
    [
        "Reels / Shorts (1080x1920)",
        "Instagram Post (1080x1080)",
        "YouTube (1920x1080)"
    ]
)

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
    custom_seconds = st.number_input(
        "Custom Time Frame (Seconds mein):",
        min_value=5,
        max_value=300,
        value=25,
        step=1
    )

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Generate Instant MP4 Video", type="primary", use_container_width=True)

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
            # Lazy-load heavy video/image libraries only when Generate is clicked
            progress_text.info("⚙️ Video engine load ho raha hai...")
            from PIL import Image
            from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

            voice_mapping = {
                "Swara (Hindi - Female)": "hi-IN-SwaraNeural",
                "Madhur (Hindi - Male)": "hi-IN-MadhurNeural",
                "Aria (English - Female)": "en-US-AriaNeural",
                "Guy (English - Male)": "en-US-GuyNeural",
            }
            selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                temp_audio_path = tmp_audio.name

            # Step 1: Generate Voiceover with Auto-Speed Sync
            progress_text.info("🎙️ Step 1/3: Voiceover aur speed sync calculate ho raha hai...")
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

                progress_text.info(f"⚡ Voice speed ko {target_duration:.0f}s video ke mutabiq ({rate_str}) adjust kiya ja raha hai...")
                asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path, rate_str=rate_str))
            else:
                target_duration = None

            # Step 2: Process Ordered Images
            progress_text.info("🖼️ Step 2/3: Images ko aapke sequence mein render kiya ja raha hai...")
            
            if "1080x1920" in video_format:
                target_size = (1080, 1920)
            elif "1080x1080" in video_format:
                target_size = (1080, 1080)
            else:
                target_size = (1920, 1080)

            for img_data in st.session_state.ordered_images:
                img = Image.open(BytesIO(img_data["bytes"])).convert("RGB")
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    img.save(tmp_img.name, format="JPEG", quality=95)
                    temp_image_paths.append(tmp_img.name)

            # Step 3: Merge Images & Audio into Final MP4 Video
            progress_text.info("🎬 Step 3/3: Images aur Voiceover ko jod kar MP4 video ban rahi hai...")
            
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
            
            progress_text.empty()
            st.success(f"🎉 Video ({final_duration:.1f} sec) successfully ban gayi hai!")
            
            st.video(final_video_path)
            
            with open(final_video_path, "rb") as vid_file:
                video_bytes = vid_file.read()
            
            st.download_button(
                label=f"📥 Download {int(final_duration)}s Video (.mp4)",
                data=video_bytes,
                file_name=f"delhi_ncr_promo_{int(final_duration)}s.mp4",
                mime="video/mp4",
                use_container_width=True
            )

        except Exception as e:
            progress_text.empty()
            st.error(f"Video banane mein error aaya: {e}")
