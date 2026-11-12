import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
import urllib.parse
import time

st.set_page_config(
    page_title="TGM Pro Multi-Image Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Multi-Scene AI Media Generator")
st.markdown("Yahan aap multiple promotional images aur voiceover script generate kar sakte hain. *(Note: Free server limit ki wajah se har image ke beech 45 seconds ka delay rahega taaki error na aaye)*")

# Initialize Session State for image prompts
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = [
        "A candid raw street photo of a worried small business owner looking at his empty shop, customers passing by without noticing, realistic lighting, 4k",
        "A stunning professional business website appearing on a sleek laptop and smartphone screen, bright modern interior, photorealistic, 8k",
        "Showcasing beautiful website designs, responsive mobile layouts, and a clean WhatsApp chat icon on screen, professional commercial photography"
    ]

with st.form("multi_media_form"):
    st.subheader("🖼️ Image Prompts (Scenes)")
    
    updated_prompts = []
    for i, prompt_text in enumerate(st.session_state.image_prompts):
        p = st.text_area(f"Scene {i+1} Image Prompt:", value=prompt_text, height=75, key=f"prompt_{i}")
        updated_prompts.append(p)
    
    st.session_state.image_prompts = updated_prompts

    col_add, col_clear = st.columns(2)
    with col_add:
        add_btn = st.form_submit_button("➕ Add Another Image Prompt")
    with col_clear:
        clear_btn = st.form_submit_button("🗑️ Reset Prompts")

    st.markdown("---")
    st.subheader("🗣️ Voiceover Script & Settings")
    
    voice_text = st.text_area(
        "Voiceover Script (Jo audio mein bolna hai):",
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

    submitted = st.form_submit_button("🚀 Generate All Images & Voiceover")

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
    if not voice_text.strip():
        st.warning("Kripya voiceover script zaroor bharein!")
    else:
        progress_text = st.empty()
        
        try:
            # 1. Generate Voiceover Audio First
            progress_text.text("🎙️ Voiceover audio generate ho raha hai...")
            voice_mapping = {
                "Swara (Hindi - Female, Natural & Warm)": "hi-IN-SwaraNeural",
                "Madhur (Hindi - Male, Deep & Professional)": "hi-IN-MadhurNeural",
                "Aria (English - Female, Professional)": "en-US-AriaNeural",
                "Guy (English - Male, Conversational)": "en-US-GuyNeural",
            }
            selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_audio_path = tmp_file.name

            asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path))

            # 2. Generate Images one by one with strict 45 seconds gap
            st.success("🎉 Voiceover tayar hai! Ab images generate ho rahi hain (Server ki strict limit ki wajah se har image ke baad 45 seconds ka gap liya jayega)...")
            
            st.markdown("### 🖼️ Generated Scenes (Images):")
            for idx, prompt in enumerate(st.session_state.image_prompts):
                if prompt.strip():
                    if idx > 0:
                        # 45 seconds wait to strictly respect the new server limit
                        for remaining in range(45, 0, -1):
                            progress_text.text(f"⏳ Server rate-limit cooldown: Agli image {remaining} seconds mein banegi...")
                            time.sleep(1)
                    
                    progress_text.text(f"🎨 Scene {idx+1} generate ho raha hai...")
                    
                    refined_prompt = prompt + ", raw photo, hyper-detailed skin texture, DSLR, Fujifilm XT3, no painting, no cartoon"
                    encoded_prompt = urllib.parse.quote(refined_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed_val + idx}&model=flux&nologo=true&private=true"
                    
                    st.markdown(f"**Scene {idx+1}:** *{prompt}*")
                    st.image(image_url, caption=f"Scene {idx+1} Generated Image", use_container_width=True)
                    st.markdown("---")

            progress_text.text("✅ Sabhi images aur audio successfully ban gaye hain!")

            # Display Audio
            st.markdown("### 🔊 Complete Voiceover Audio:")
            st.audio(temp_audio_path, format="audio/mp3")

            with open(temp_audio_path, "rb") as f:
                audio_bytes = f.read()

            st.download_button(
                label="📥 Download Full Voiceover Audio (.mp3)",
                data=audio_bytes,
                file_name="tgm_complete_voiceover.mp3",
                mime="audio/mp3"
            )

        except Exception as e:
            st.error(f"Error: {e}")
