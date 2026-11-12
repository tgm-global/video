import streamlit as st
from gtts import gTTS
import os
from io import BytesIO

st.set_page_config(
    page_title="TGM AI Image & Voice Studio",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ TGM AI Image & Voice Generator")
st.markdown("Aap apna prompt aur voiceover script daalein, aur AI Image ke sath Voiceover audio generate karein!")

with st.form("media_form"):
    # Image prompt
    image_prompt = st.text_area(
        "🖼️ Image Prompt (English mein behtar hai):",
        value="Cinematic shot of an Indian shopkeeper smiling while looking at a modern website on a laptop, professional lighting, 4k",
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
        lang_choice = st.selectbox("Language / Accent:", ["hi (Hindi)", "en (English)"])
    with col2:
        # Note: gTTS default voice natural hoti hai; hum ise language code se control karte hain
        voice_type = st.selectbox("Voice Style:", ["Standard Voice"])

    submitted = st.form_submit_button("🚀 Generate Image & Audio")

if submitted:
    if not image_prompt.strip() or not voice_text.strip():
        st.warning("Kripya image prompt aur voiceover script dono bharein!")
    else:
        with st.spinner("AI Image aur Audio generate ho rahe hain..."):
            try:
                # 1. AI Image URL generate karna (100% free & instant via Pollinations API)
                formatted_prompt = image_prompt.replace(" ", "%20")
                image_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width=1080&height=1920&nologo=true"
                
                # 2. Audio Voiceover generate karna (via gTTS)
                lang_code = lang_choice.split(" ")[0]
                tts = gTTS(text=voice_text, lang=lang_code, slow=False)
                
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                
                st.success("🎉 Aapka Content Tayar Hai!")
                
                # Display Image
                st.markdown("### 🖼️ Generated AI Image:")
                st.image(image_url, caption="Generated Promotional Image", use_container_width=True)
                
                # Display Audio Player & Download
                st.markdown("### 🔊 Generated Voiceover Audio:")
                st.audio(audio_bytes, format="audio/mp3")
                
                st.download_button(
                    label="📥 Download Voiceover Audio (.mp3)",
                    data=audio_bytes,
                    file_name="tgm_voiceover.mp3",
                    mime="audio/mp3"
                )
                
                st.info("💡 **Tip:** Aap is image aur audio ko kisi bhi free mobile app (jaise CapCut ya InShot) mein daalkar 10 second ki professional promotional reel bana sakte hain!")
                
            except Exception as e:
                st.error(f"Kuch error aa gaya: {e}")
