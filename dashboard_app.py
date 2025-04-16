# import streamlit as st
# import requests
# import time
# import base64
# from PIL import Image
# from io import BytesIO

# st.title("Posture Monitoring")

# # Create a placeholder for the image
# image_placeholder = st.empty()
# score_placeholder = st.empty()
# summary_placeholder = st.empty()
# tip_placeholder = st.empty()

# is_monitoring = st.session_state.get("is_monitoring", False)

# def get_latest_result():
#     try:
#         res = requests.get("http://192.168.68.103:5000/latest")
#         if res.status_code == 200:
#             return res.json()
#     except Exception as e:
#         st.warning("Server not responding.")
#     return None

# # Button to start/stop
# if st.button("Start Monitoring" if not is_monitoring else "Stop Monitoring"):
#     is_monitoring = not is_monitoring
#     st.session_state["is_monitoring"] = is_monitoring

# # Live update loop
# while st.session_state.get("is_monitoring", False):
#     result = get_latest_result()
#     if result:
#         # Decode and display image
#         img_bytes = base64.b64decode(result["image"])
#         img = Image.open(BytesIO(img_bytes))
#         image_placeholder.image(img, caption="Posture Detection", use_column_width=True)

#         # Show posture info
#         score_placeholder.markdown(f"**Posture Score:** {result['score']}/10")
#         summary_placeholder.markdown(f"**Summary:** {result['summary']}")
#         tip_placeholder.markdown(f"**Tip:** {result['tip']}")
    
#     time.sleep(2)
import streamlit as st
import requests
import time
import base64
from PIL import Image
from io import BytesIO

st.title("Posture Monitoring")

# Placeholders for dynamic content
image_placeholder = st.empty()
score_placeholder = st.empty()
summary_placeholder = st.empty()
tip_placeholder = st.empty()

# Initialize session state
if "is_monitoring" not in st.session_state:
    st.session_state["is_monitoring"] = False

# Button logic
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Start Monitoring") and not st.session_state["is_monitoring"]:
        st.session_state["is_monitoring"] = True

with col2:
    if st.button("Stop Monitoring") and st.session_state["is_monitoring"]:
        st.session_state["is_monitoring"] = False

# Function to fetch latest image & analysis
def get_latest_result():
    try:
        res = requests.get("http://192.168.68.103:5000/latest")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.warning("Server not responding.")
    return None

# Simulate live update with Streamlit rerun
if st.session_state["is_monitoring"]:
    result = get_latest_result()
    if result:
        img_bytes = base64.b64decode(result["image"])
        img = Image.open(BytesIO(img_bytes))
        image_placeholder.image(img, caption="Posture Detection", use_container_width=True)

        score_placeholder.markdown(f"**Posture Score:** {result['score']}/10")
        summary_placeholder.markdown(f"**Summary:** {result['summary']}")
        tip_placeholder.markdown(f"**Tip:** {result['tip']}")

    # Auto-refresh every 2 seconds
    time.sleep(10)
    st.rerun()