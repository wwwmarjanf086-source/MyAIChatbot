
import streamlit as st
import time
from google import genai

# Page settings
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 My AI Chatbot")
st.caption("Your personal AI assistant, powered by Gemini.")

# Connect to Gemini
try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"],
        http_options={"timeout": 60000}
    )
except Exception as error:
    st.error(f"Connection setup failed: {error}")
    st.stop()

# Conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_interaction_id" not in st.session_state:
    st.session_state.previous_interaction_id = None

# Sidebar
if st.sidebar.button("New conversation"):
    st.session_state.messages = []
    st.session_state.previous_interaction_id = None
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask me anything...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:
            with st.spinner("Gemini is thinking... 🤔"):

                request = {
                    "model": "gemini-3.8-flash",
                    "input": prompt,
                    "background": True
                }

                if st.session_state.previous_interaction_id:
                    request["previous_interaction_id"] = (
                        st.session_state.previous_interaction_id
                    )

                # Start the task
                interaction = client.interactions.create(**request)

                # Check for the completed answer
                for attempt in range(90):

                    if interaction.status in (
                        "completed",
                        "failed",
                        "cancelled",
                        "requires_action"
                    ):
                        break

                    time.sleep(2)

                    interaction = client.interactions.get(
                        id=interaction.id
                    )

                # Display the result
                if interaction.status == "completed":

                    answer = (interaction.output_text or "").strip()

                    if answer:
                        st.markdown(answer)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                        st.session_state.previous_interaction_id = (
                            interaction.id
                        )
                    else:
                        st.warning("Gemini returned an empty response.")

                elif interaction.status == "in_progress":
                    st.warning(
                        "Gemini is still working. Please try again shortly."
                    )

                else:
                    st.error(
                        f"Interaction status: {interaction.status}"
                    )

        except Exception as error:
            st.error(f"Gemini connection error: {error}")
