import streamlit as st
import time

# Page Configuration
st.set_page_config(
    page_title="Delhi NCR Web Design - Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Delhi NCR Web Design - AI Video Studio")
st.markdown("Aap apna custom promotional video prompt daalein aur video generate karein!")

# Default Prompt jo aapne diya tha
default_prompt = (
    "Create a premium 35-second vertical (9:16) promotional video for Delhi NCR Web Design. "
    "Show Indian shopkeepers, restaurant and salon owners discovering the benefits of having a professional website. "
    "Display stunning website designs on laptops and smartphones with blue-white-black branding and cinematic transitions."
)

# User Input Form
with st.form("video_form"):
    user_prompt = st.text_area("Video Prompt:", value=default_prompt, height=150)
    aspect_ratio = st.selectbox("Aspect Ratio:", ["9:16 (Vertical / Reels)", "16:9 (Landscape)"])
    
    submitted = st.form_submit_button("🚀 Generate Video")

if submitted:
    if not user_prompt.strip():
        st.warning("Kripya koi prompt darj karein!")
    else:
        with st.spinner("Video render ho raha hai... Kripya kuch samay pratiksha karein (Yeh kuch second le sakta hai)..."):
            # Simulation / API integration placeholder
            time.sleep(4)
            
            st.success("🎉 Aapka video successfully generate ho gaya hai!")
            
            # Simulated Video Result Display
            st.markdown("### 📥 Download Link:")
            st.info("Aapka 9:16 vertical promotional video tayar hai.")
            
            # Download button simulation
            st.download_button(
                label="📥 Download Video (.mp4)",
                data=b"Mock video binary data for Delhi NCR Web Design",
                file_name="delhi_ncr_web_design_promo.mp4",
                mime="video/mp4"
            )
