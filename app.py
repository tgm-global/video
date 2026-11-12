import streamlit as st
from gradio_client import Client
import os

st.set_page_config(
    page_title="TGM Real AI Video Studio",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 TGM Real AI Video Generator")
st.markdown("Text prompt daalein aur **bilkul asli AI video** free mein generate karein!")

with st.form("real_video_form"):
    prompt = st.text_area(
        "Apna Video Prompt Likhein (English mein behtar result aata hai):",
        placeholder="e.g., Cinematic shot of an Indian shopkeeper smiling while looking at a modern website on a laptop, warm lighting, 4k",
        height=120
    )
    
    seed = st.number_input("Seed (Alag variations ke liye number badlein):", value=42, step=1)
    submitted = st.form_submit_button("🚀 Generate Real AI Video")

if submitted:
    if not prompt.strip():
        st.warning("Kripya pehle koi prompt likhein!")
    else:
        with st.spinner("Free AI Server se video generate ho rahi hai... Ismein 1 se 2 minute lag sakte hain, kripya intezaar karein..."):
            try:
                # Public Hugging Face Space se connect karna (Bina API key ke)
                client = Client("damo-vilab/modelscope-text-to-video-synthesis")
                
                # Real AI Video Generate karna
                video_path = client.predict(
                    prompt,       # Text prompt
                    int(seed),    # Seed value
                    16,           # Number of frames
                    25,           # Inference steps
                    api_name="/predict"
                )
                
                # Agar output tuple ya dict mein aaye toh file path nikalna
                if isinstance(video_path, (list, tuple)):
                    video_path = video_path[0]
                elif isinstance(video_path, dict):
                    video_path = video_path.get("video", "")

                if video_path and os.path.exists(video_path):
                    st.success("🎉 Aapki asli AI video tayar hai!")
                    
                    # Browser mein video play karna
                    st.video(video_path)
                    
                    # Real MP4 file download ke liye dena
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Real Video (.mp4)",
                            data=file,
                            file_name="tgm_ai_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Server busy hone ki wajah se video nahi ban paayi. Kripya thodi der baad dobara try karein.")
                    
            except Exception as e:
                st.error(f"Free AI server abhi overload hai ya error aaya hai: {e}")
                st.info("Tip: Free public servers par traffic zyada hone par kabhi-kabhi error aata hai, 1 minute baad 'Generate' par dobara click karein.")
