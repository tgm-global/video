import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
import urllib.parse

st.set_page_config(
    page_title="TGM Pro Multi-Image Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Multi-Scene AI Media Generator")
st.markdown("Yahan aap jitni chahein utni promotional images ke prompts add kar sakte hain, saath mein voiceover script bhi!")

# Initialize Session State for image prompts if not already present
if "image_prompts" not in st.session_state:
    st.session_state.image_prompts = [
        "A candid raw street photo of a worried small business owner looking at his empty shop, customers passing by without noticing, realistic lighting, 4k", # Image 1 default
        "A stunning professional business website appearing on a sleek laptop and smartphone screen, bright modern interior, photorealistic, 8k", # Image 2 default
        "Showcasing beautiful website designs, responsive mobile layouts, and a clean WhatsApp chat icon on screen, professional commercial photography" # Image 3 default
    ]

with st.form("multi_media_form"):
    st.subheader("🖼️ Image Prompts (Scenes)")
    
    # Render text areas dynamically for each prompt in session state
    updated_prompts = []
    for i, prompt_text in enumerate(st.session_state.image_prompts):
        p = st.text_area(f"Scene {i+1} Image Prompt:", value=prompt_text, height=75, key=f"prompt_{i}")
        updated_prompts.append(p)
    
    # Update session state values
    st.session_state.image_prompts = updated_prompts

    # Buttons layout inside form (using columns for 'Add Image' functionality via rerun trick or standard flow)
    col_add, col_clear = st.columns(2)
    with col_add:
        add_btn = st.form_submit_button("➕ Add Another Image Prompt")
    with col_clear:
        clear_btn = st.form_submit_button("🗑️ Reset Prompts")

    st.markdown("---")
    st.subheader("🗣️ Voiceover Script & Settings")
    
    voice_text = st.text_area(
        "Voiceover Script (Jo audio mein bolna hai):",
        value="Kya aapka business abhi tak online nahi hai? Aaj hi banwayein ek professional website sirf nau sau ninaanve rupaye mein!",
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

# Handle Add/Reset button clicks outside or right after form submission logic
if add_btn:
    st.session_state.image_prompts.append("Describe your next scene here (e.g., Happy business owner receiving online orders)...")
    st.rerun()

if clear_btn:
    st.session_state.image_prompts = ["A candid raw street photo of a small business owner looking worried..."]
    st.rerun()

# Async function for Edge-TTS
async def generate_natural_audio(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name, rate="+0%", pitch="+0Hz")
    await communicate.save(output_file)

if submitted and not add_btn and not clear_btn:
    if not voice_text.strip():
        st.warning("Kripya voiceover script zaroor bharein!")
    else:
        with st.spinner("Aapki saari images aur voiceover generate ho rahe hain... Kripya thoda intezaar karein!"):
            try:
                st.success("🎉 Saara Content Successfully Tayar Ho Gaya Hai!")
                
                # 1. Generate and Display All Images
                st.markdown("### 🖼️ Generated Scenes (Images):")
                for idx, prompt in enumerate(st.session_state.image_prompts):
                    if prompt.strip():
                        refined_prompt = prompt + ", raw photo, hyper-detailed skin texture, DSLR, Fujifilm XT3, no painting, no cartoon"
                        encoded_prompt = urllib.parse.quote(refined_prompt)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed_val + idx}&model=flux&nologo=true&private=true"
                        
                        st.markdown(f"**Scene {idx+1}:** *{prompt}*")
                        st.image(image_url, caption=f"Scene {idx+1} Generated Image", use_container_width=True)
                        st.markdown("---")

                # 2. Generate and Display Voiceover Audio
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
