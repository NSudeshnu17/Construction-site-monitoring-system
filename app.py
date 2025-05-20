import streamlit as st
from utils.auth import login_user, register_user, check_user_exists
from model.load_model import detect_objects
from utils.data_utils import save_detection_data, plot_compliance_trends
import os
from PIL import Image
import datetime
import cv2
from tempfile import NamedTemporaryFile

# Optional fix for torch watchers on some systems
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

st.set_page_config(page_title="Construction Safety Monitor", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ───────────────────────────────────────────────
# LANDING PAGE
# ───────────────────────────────────────────────
def landing_page():
    st.title("🏗️ Construction Site Safety Monitor")
    st.image(
        "https://cdn.pixabay.com/photo/2016/03/09/09/30/architect-1245725_960_720.jpg",
        use_container_width=True,
    )
    st.subheader("Welcome to the Construction Safety Monitoring Platform")
    st.markdown(
        "Detect PPE and track safety compliance with AI-powered video and photo analysis."
    )

    st.markdown("#### Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.show_register = False
            st.success("Login successful!")
        else:
            st.error("Invalid credentials!")

    st.markdown("Don't have an account?")
    if st.button("Register here"):
        st.session_state.show_register = True


# ───────────────────────────────────────────────
# REGISTRATION PAGE
# ───────────────────────────────────────────────
def registration_page():
    st.title("Register New Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register"):
        if check_user_exists(new_user):
            st.warning("User already exists.")
        else:
            register_user(new_user, new_pass)
            st.session_state.authenticated = True
            st.session_state.user = new_user
            st.session_state.show_register = False
            st.success("Registration successful. Redirecting to dashboard...")


# ───────────────────────────────────────────────
# DASHBOARD PAGE
# ───────────────────────────────────────────────
def dashboard():
    st.sidebar.title(f"👷 Hello, {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.experimental_rerun()

    tab = st.sidebar.radio("Navigation", ["📸 Upload & Detect", "📊 Compliance Trends"])

    if tab == "📸 Upload & Detect":
        st.title("Upload Image or Video for Safety Detection")
        file = st.file_uploader(
            "Upload photo or video", type=["jpg", "jpeg", "png", "mp4"]
        )

        if file:
            save_path = os.path.join("uploads", file.name)
            with open(save_path, "wb") as f:
                f.write(file.read())

            if file.type.startswith("image"):
                image = Image.open(save_path)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                output_image, detections = detect_objects(image)
                st.image(output_image, caption="Detected", use_container_width=True)
                save_detection_data(detections)
                st.success("Detection complete and logged.")

            elif file.type.endswith("mp4"):
                st.video(save_path)
                st.info("Processing video...")

                cap = cv2.VideoCapture(save_path)
                frame_count = 0
                all_detections = []
                sampled_images = []

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1

                    # Process 1 frame every 15 to save time
                    if frame_count % 15 == 0:
                        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        output_img, detections = detect_objects(image)
                        all_detections.extend(detections)

                        if len(sampled_images) < 5:
                            sampled_images.append(output_img.copy())

                cap.release()
                save_detection_data(all_detections)
                st.success(f"Processed {frame_count} frames. Detection saved.")

                for idx, img in enumerate(sampled_images):
                    st.image(
                        img, caption=f"Detected Frame {idx+1}", use_container_width=True
                    )

    elif tab == "📊 Compliance Trends":
        st.title("Weekly / Monthly Safety Analysis")
        st.pyplot(plot_compliance_trends())


# ───────────────────────────────────────────────
# APP ROUTING
# ───────────────────────────────────────────────
if "show_register" not in st.session_state:
    st.session_state.show_register = False

if not st.session_state.authenticated:
    if st.session_state.show_register:
        registration_page()
    else:
        landing_page()
else:
    dashboard()
