import streamlit as st
import requests
import time

API_URL = "http://chat-api:8000"

st.set_page_config(page_title="💬 Chat Room", page_icon="💬", layout="centered")
st.title("💬 Real-Time Chat Room")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Settings")
    username = st.text_input("Your Username", value="User1")
    room = st.text_input("Room Name", value="general")
    auto_refresh = st.toggle("Auto Refresh (3s)", value=True)
    st.markdown("---")
    st.caption("Powered by FastAPI + Redis")

st.subheader(f"📨 Room: `{room}`")
with st.form("send_form", clear_on_submit=True):
    message = st.text_input("Type your message...", placeholder="Hello everyone!")
    submitted = st.form_submit_button("Send 🚀")
    if submitted and message.strip():
        try:
            res = requests.post(
                f"{API_URL}/send",
                params={"room": room, "username": username, "message": message}
            )
            if res.status_code == 200:
                st.success("Message sent!")
            else:
                st.error(f"Failed: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"API Error: {e}")

st.markdown("---")
st.subheader("📜 Chat History")

try:
    res = requests.get(f"{API_URL}/history/{room}")
    if res.status_code == 200:
        data = res.json()
        messages = data.get("messages", [])
        if messages:
            for msg in messages:
                with st.chat_message("human"):
                    st.markdown(f"**{msg['username']}**: {msg['message']}")
        else:
            st.info("No messages yet. Be the first to say something! 👋")
    else:
        st.error("Could not fetch messages.")
except Exception as e:
    st.warning(f"Waiting for API... ({e})")

if auto_refresh:
    time.sleep(3)
    st.rerun()