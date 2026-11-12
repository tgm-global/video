import streamlit as st
import asyncio
import edge_tts
import os
import tempfile

st.set_page_config(
    page_title="TGM Real AI Studio",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ TGM Real AI Image & Realistic Voice Generator")
st.markdown("Ultra-realistic AI Images aur bilkul aisi aawaz jaisi professional voiceover artist bol raha ho!")

with st.form("media_form"):
    # Image prompt
    image_prompt = st.text_area(
        "🖼️ Image Prompt (Detailed English mein):",
        value="A professional real photo of an Indian shopkeeper smiling proudly in his shop, showing a modern website on a sleek laptop and smartphone, bright indoor lighting, 4k, DSLR photography",
        height=100
    )
    
    # Voiceover script
    voice_text = st.text_area(
        "🗣️ Voiceover Script (Jo audio mein bolna hai):",
        value="Kya aapka business online nahi hai? Ab banwayein professional website sirf nau sau ninaanve rupaye mein!",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        # Microsoft Edge ki natural voices (Hindi aur English)
        voice_option = st.selectbox(
            "Select Realistic Voice:", 
            [
                "Madhur (Hindi - Male, Natural)", 
                "Swara (Hindi - Female, Natural)", 
                "Aria (English - Female, Natural)", 
                "Guy (English - Male, Natural)"
            ]
        )
    with col2:
        seed_val = st.number_input("Image Variation Seed:", value=42, step=1)

    submitted = st.form_submit_button("🚀 Generate Realistic Image & Audio")

# Helper function to run async edge-tts
async def generate_edge_audio(text, voice_name, output_file):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

if submitted:
    if not image_prompt.strip() or not voice_text.strip():
        st.warning("Kripya image prompt aur voiceover script dono bharein!")
    else:
      with st.spinner("Ultra-realistic AI image aur Natural Voice generate ho rahi hain..."):
        try:
          # 1. Ultra-realistic Image via Pollinations Flux Model
          formatted_prompt = image_prompt.replace(" ", "%20")
          image_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width=1080&height=1920&seed={seed_val}&model=flux&nologo=true"

          # 2. Select correct voice mapping for Edge TTS
          voice_mapping = {
              "Madhur (Hindi - Male, Natural)": "hi-IN-MadhurNeural",
              "Swara (Hindi - Female, Natural)": "hi-IN-SwaraNeural",
              "Aria (English - Female, Natural)": "en-US-AriaNeural",
              "Guy (English - Male, Natural)": "en-US-GuyNeural",
          }
          selected_voice = voice_mapping.get(voice_option, "hi-IN-SwaraNeural")

          # Temporary file for audio
          with tempfile.NamedTemporaryFile(
              delete=False, suffix=".mp3"
          ) as tmp_file:
            temp_audio_path = tmp_file.name

          # Generate audio using edge-tts
          asyncio.run(
              generate_edge_audio(voice_text, selected_voice, temp_audio_path)
          )

          st.success("🎉 Aapka Realistic Content Tayar Hai!")

          # Display Image
          st.markdown("### 🖼️ Generated Real AI Image:")
          st.image(
              image_url,
              caption="Ultra-Realistic Generated Image",
              use_container_width=True,
          )

          # Display Audio Player & Download
          st.markdown("### 🔊 Realistic Neural Voiceover Audio:")
          st.audio(temp_audio_path, format="audio/mp3")

          with open(temp_audio_path, "rb") as f:
            audio_bytes = f.read()

          st.download_button(
              label="📥 Download Realistic Voiceover (.mp3)",
              data=audio_bytes,
              file_name="tgm_realistic_voiceover.mp3",
              mime="audio/mp3",
          )

        except Exception as e:
          st.error(f"Kuch error aa gaya: {e}")
