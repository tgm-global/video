import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
import urllib.parse

st.set_page_config(
    page_title="TGM Pro Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Ultra-Realistic Media Generator")
st.markdown("Bilkul asli DSLR photo aur professional human-like voiceover generate karein!")

with st.form("media_form"):
    # Image prompt with strong realistic photography enforcement
    image_prompt = st.text_area(
        "🖼️ Image Description (Detail mein likhein):",
        value="A candid raw street photo of a confident Indian shopkeeper smiling inside his modern retail shop, holding a sleek laptop displaying a clean website design, natural window lighting, shot on 35mm lens, photorealistic, 8k resolution, realistic skin texture",
        height=100
    )
    
    # Voiceover script
    voice_text = st.text_area(
        "🗣️ Voiceover Script (Natural pauses ke sath likhein):",
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
        seed_val = st.number_input("Random Seed (New look ke liye number badlein):", value=123, step=1)

    submitted = st.form_submit_button("🚀 Generate Ultra-Realistic Media")

# Async function to generate natural edge-tts with adjusted pitch/rate
async def generate_natural_audio(text, voice_name, output_file):
    # Adding slight adjustments if supported, or standard clean communication
    communicate = edge_tts.Communicate(text, voice_name, rate="+0%", pitch="+0Hz")
    await communicate.save(output_file)

if submitted:
    if not image_prompt.strip() or not voice_text.strip():
        st.warning("Kripya dono fields bharein!")
    else:
        with st.spinner("Ultra-realistic image aur human-like voice taiyar ho rahi hain..."):
            try:
                # 1. Enforcing Pollinations Flux with strict realism tags
                refined_prompt = image_prompt + ", raw photo, hyper-detailed skin texture, DSLR, Fujifilm XT3, no painting, no cartoon"
                encoded_prompt = urllib.parse.quote(refined_prompt)
                
                # Using direct high-quality pollinations URL with explicit model
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed_val}&model=flux&nologo=true&private=true"

                # 2. Voice Mapping
                voice_mapping = {
                    "Swara (Hindi - Female, Natural & Warm)": "hi-IN-SwaraNeural",
                    "Madhur (Hindi - Male, Deep & Professional)": "hi-IN-MadhurNeural",
                    "Aria (English - Female, Professional)": "en-US-AriaNeural",
                    "Guy (English - Male, Conversational)": "en-US-GuyNeural",
                }
                selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

                # Temporary file for audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    temp_audio_path = tmp_file.name

                # Generate audio
                asyncio.run(generate_natural_audio(voice_text, selected_voice, temp_audio_path))

                st.success("🎉 Aapka Content Tayar Hai!")

                # Display Image
                st.markdown("### 🖼️ Ultra-Realistic Photo:")
                st.image(image_url, caption="Generated Real-Style Photo", use_container_width=True)
                
                # Display Audio
                st.markdown("### 🔊 Natural Voiceover Audio:")
                st.audio(temp_audio_path, format="audio/mp3")

                with open(temp_audio_path, "rb") as f:
                    audio_bytes = f.read()

                st.download_button(
                    label="📥 Download Natural Voiceover (.mp3)",
                    data=audio_bytes,
                    file_name="tgm_natural_voice.mp3",
                    mime="audio/mp3"
                )

            except Exception as e:
                st.error(f"Error: {e}")
