import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
import urllib.parse
import time
import requests
from PIL import Image
from io import BytesIO
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(
    page_title="TGM Pro Auto-Video Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Complete AI Video Studio")
st.markdown("Images aur Voiceover ko jod kar automatic **MP4 Promotional Video** banayein!")

# Initialize Session State for image prompts
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = [
        "A candid raw street photo of a worried small business owner looking at his empty shop, customers passing by without noticing, realistic lighting, 4k",
        "A stunning professional business website appearing on a sleek laptop and smartphone screen, bright modern interior, photorealistic, 8k",
        "Showcasing beautiful website designs, responsive mobile layouts, and a clean WhatsApp chat icon on screen, professional commercial photography"
    ]

with st.form("multi_media_form"):
    st.subheader("🖼️ Scene Prompts")
    
    updated_prompts = []
    for i, prompt_text in enumerate(st.session_state.image_prompts):
        p = st.text_area(f"Scene {i+1} Prompt:", value=prompt_text, height=75, key=f"prompt_{i}")
        updated_prompts.append(p)
    
    st.session_state.image_prompts = updated_prompts

    col_add, col_clear = st.columns(2)
    with col_add:
        add_btn = st.form_submit_button("➕ Add Another Scene")
    with col_clear:
        clear_btn = st.form_submit_button("🗑️ Reset Scenes")

    st.markdown("---")
    st.subheader("🗣️ Voiceover Script & Settings")
    
    voice_text = st.text_area(
        "Voiceover Script (Jo video mein bolna hai):",
        value="Kya aapka business abhi tak online nahi hai? Aaj hi banwayein ek professional website, woh bhi sirf nau sau ninaanve rupaye mein!",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        voice_option = st.selectbox(
            "Select Realistic Voice:", 
            [
                "Swara (Hindi - Female, Natural & Warm)", 
                "Madhur (Hindi - Male, Deep & Professional)", 
                "Aria (English - Female, Professional)", 
                "Guy (English - Male, Conversational)"
            ]
        )
    with col2:
        seed_val = st.number_input("Random Seed:", value=123, step=1)

    submitted = st.form_submit_button("🚀 Generate Complete MP4 Video")

if add_btn:
    st.session_state.image_prompts.append("Describe your next scene here...")
    st.rerun()

if clear_btn:
    st.session_state.image_prompts = ["A candid raw street photo of a small business owner looking worried..."]
    st.rerun()

async def generate_natural_audio(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name, rate="+0%", pitch="+0Hz")
    await communicate.save(output_file)

if submitted and not add_btn and not clear_btn:
    valid_prompts = [p.strip() for p in st.session_state.image_prompts if p.strip()]
    
    if not voice_text.strip() or not valid_prompts:
        st.warning("Kripya kam se kam ek image prompt aur voiceover script zaroor bharein!")
    else:
        progress_text = st.empty()
        temp_image_paths = []
        
        try:
            # 1. Generate Voiceover Audio First
            progress_text.text("🎙️ Step 1/3: Voiceover audio generate ho raha hai...")
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

            # 2. Download & Save Each Image Locally
            for idx, prompt in enumerate(valid_prompts):
                if idx > 0:
                    for remaining in range(45, 0, -1):
                        progress_text.text(f"⏳ Server limit cooldown: Scene {idx+1} ke liye {remaining} seconds bache hain...")
                        time.sleep(1)
                
                progress_text.text(f"🎨 Step 2/3: Scene {idx+1}/{len(valid_prompts)} download ho raha hai...")
                
                refined_prompt = prompt + ", raw photo, hyper-detailed skin texture, DSLR, Fujifilm XT3, no painting, no cartoon"
                encoded_prompt = urllib.parse.quote(refined_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed_val + idx}&model=flux&nologo=true&private=true"
                
                response = requests.get(image_url, timeout=60)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    # Ensure uniform resolution (1080x1920) for clean video merging
                    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                        img.save(tmp_img.name, format="JPEG", quality=95)
                        temp_image_paths.append(tmp_img.name)
                else:
                    st.error(f"Scene {idx+1} download fail ho gaya (Status: {response.status_code}).")

            if not temp_image_paths:
                st.error("Koi bhi image download nahi ho payi, isliye video nahi ban sakti.")
            else:
                # 3. Merge Images & Audio into Final MP4 Video
                progress_text.text("🎬 Step 3/3: Saari scenes aur audio ko jod kar MP4 video render ho rahi hai...")
                
                audio_clip = AudioFileClip(temp_audio_path)
                total_duration = audio_clip.duration
                duration_per_image = total_duration / len(temp_image_paths)
                
                clips = [ImageClip(img_path).set_duration(duration_per_image) for img_path in temp_image_paths]
                final_video = concatenate_videoclips(clips, method="compose")
                final_video = final_video.set_audio(audio_clip)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                    final_video_path = tmp_vid.name
                
                # Render MP4 file
                final_video.write_videofile(
                    final_video_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                # Close clips to free memory
                audio_clip.close()
                final_video.close()
                
                progress_text.text("✅ Aapki Complete Promotional Video Tayar Hai!")
                st.success("🎉 Badhai ho! Aapki final MP4 video successfully render ho gayi hai.")
                
                # Display Final Video
                st.markdown("### 🎬 Final Promotional Video:")
                st.video(final_video_path)
                
                with open(final_video_path, "rb") as vid_file:
                    video_bytes = vid_file.read()
                
                st.download_button(
                    label="📥 Download Final Promotional Video (.mp4)",
                    data=video_bytes,
                    file_name="delhi_ncr_web_design_promo.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"Video banane mein error aaya: {e}")
