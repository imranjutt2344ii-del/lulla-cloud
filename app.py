import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Set up webpage configuration
st.set_page_config(
    page_title="Pro AI Video Generator", 
    page_icon="🎬", 
    layout="centered"
)

st.title("🎬 High-Precision AI Video Generator")
st.caption("Powered by Google Veo 3.1 (Image-to-Video & Text-to-Video)")

# Retrieve API key from Streamlit secrets or sidebar input
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if not api_key:
    st.info("👈 Please enter your Gemini API Key in the sidebar to start.")
else:
    # Initialize the Google GenAI client
    client = genai.Client(api_key=api_key)

    # User inputs
    prompt = st.text_area(
        "Video Prompt / Instructions:", 
        placeholder="Describe the movement or scene (e.g., 'A camera slow pan showing this character smiling gently')..."
    )
    
    # Image reference uploader
    uploaded_image = st.file_uploader(
        "Upload Reference Image (Optional for Image-to-Video):", 
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Reference Image Preview", width=300)

    # Advanced Settings
    st.subheader("Video Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16"])
    with col2:
        duration = st.selectbox("Duration (sec)", [4, 6, 8])
    with col3:
        resolution = st.selectbox("Resolution", ["720p", "1080p"])

    negative_prompt = st.text_input(
        "Negative Prompt (Things to avoid):", 
        value="glitches, distortion, blurry, low quality, unnatural movement, flickering"
    )

    # Generation Trigger
    if st.button("Generate Video 🚀", use_container_width=True, type="primary"):
        if not prompt.strip() and not uploaded_image:
            st.warning("Please enter a prompt or upload a reference image.")
        else:
            with st.spinner("Processing generation request... (This takes ~1 to 2 minutes)"):
                try:
                    # Prepare image reference if uploaded
                    image_input = None
                    if uploaded_image:
                        image_bytes = uploaded_image.getvalue()
                        image_input = types.Image(
                            image_bytes=image_bytes,
                            mime_type=uploaded_image.type
                        )

                    # Configure video params
                    config = types.GenerateVideosConfig(
                        aspect_ratio=aspect_ratio,
                        duration_seconds=duration,
                        resolution=resolution,
                        negative_prompt=negative_prompt,
                        number_of_videos=1,
                    )

                    # Call Veo 3.1 model
                    operation = client.models.generate_videos(
                        model="veo-3.1-generate-001",
                        prompt=prompt if prompt.strip() else None,
                        image=image_input,
                        config=config,
                    )

                    # Poll until generation completes
                    while not operation.done:
                        time.sleep(10)
                        operation = client.operations.get(operation)

                    # Retrieve result
                    result = operation.result
                    generated_video = result.generated_videos[0]
                    video_uri = generated_video.video.uri
                    
                    st.success("✨ Video generated successfully!")
                    st.video(video_uri)

                except Exception as e:
                    st.error(f"Generation error: {e}")
