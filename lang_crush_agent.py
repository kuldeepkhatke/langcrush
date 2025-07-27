import os
import uuid

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from operator import itemgetter

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from streamlit_cookies_manager import EncryptedCookieManager

model = ChatGroq(model="Gemma2-9b-It", groq_api_key=os.getenv("GROQ_API_KEY"))
# -----------------------
# Initialize the chat message history

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


with_message_history = RunnableWithMessageHistory(model, get_session_history)


def create_with_message_history(language: str):
    global with_message_history
    with_message_history.invoke(
        [
            SystemMessage(
                content=f"You are a helpful AI {language} language expert and behave like a girlfriend. Try to teach new sentences around {language} language in hinglish text. keeping in mind user don't know much about {language} language."
            ),
            SystemMessage(
                content="You need to chat in a flirty manner and ask few personal questions."
            ),
            SystemMessage(
                content="keep most of the responses short but some can be longer as per need."
            ),
            SystemMessage(
                content="Need end with a follow-up question or suggestion, which tends to keep the conversation going."
            ),
            SystemMessage(content="Add some realworld basis scenarios, stories."),
            # SystemMessage(content="Ask the person about their life and day in a flirty manner in alternate questions."),
            # SystemMessage(content=f"Try to teach new sentences around {st.session_state.language} language in hinglish text. keeping in mind user don't know much about {st.session_state.language} language."),  # Adjust this value based on your needs
        ],
        config=config,
    )


# -----------------------
# Initialize cookies
# -----------------------
cookies = EncryptedCookieManager(
    prefix="langcrush_",  # All cookies will be prefixed
    password="a_strong_encryption_password",  # You can set any secure password here
)
if not cookies.ready():
    st.stop()

# -----------------------
# Generate or fetch user_id
# -----------------------
if not cookies.get("user_id"):
    user_id = str(uuid.uuid4())
    cookies["user_id"] = user_id  # Use dict-style assignment
    cookies.save()  # Save changes
else:
    user_id = cookies.get("user_id")

st.sidebar.markdown(f"🆔 **Your LangCrush ID:** `{user_id}`")

# Add LinkedIn profile image and creator info to sidebar
st.sidebar.markdown(
    """
    <div style="margin-top: 2rem; text-align: center;">
        <a href="https://www.linkedin.com/in/kuldeepkhatke/" target="_blank">
            <img src="https://media.licdn.com/dms/image/v2/D5603AQFSzxyWkpCXBw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1730832651913?e=1756339200&v=beta&t=hbhLrH38Bw_PLfmY3ajbtjS_QGbLL5L81A-5vDzzhLI">
        </a>
        <div style="font-size: 1.3rem; font-weight: bold; margin-top: 0.5rem;">
            Created by:<br>
            <a href="https://www.linkedin.com/in/kuldeepkhatke/" target="_blank" style="font-size: 1.3rem; font-weight: bold; color: #0077b5; text-decoration: none;">
                Kuldeep Khatke
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Session chat history
# -----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------
# Chat input
# -----------------------
config = {"configurable": {"session_id": user_id}}

# -----------------------
# Two-part form: Language selection (Part 1) and Chat (Part 2)
# -----------------------
if "language" not in st.session_state:
    st.session_state.language = None

# Part 1: Language selection
if st.session_state.language is None:
    st.title("💬 LangCrush – Your AI Language Tutor & Companion")
    st.markdown("#### Step 1: Choose the language you want to learn")

    # setting default language to marathi
    # st.session_state.language = "Marathi"
    # Language selection form
    with st.form("language_form"):
        lang = st.radio(
            "Languages", ["Marathi", "Hindi", "Gujarati", "Kannada"], key="lang_choice"
        )
        submitted = st.form_submit_button("Continue")
        if submitted:
            st.session_state.language = lang
            print(f"Selected language: {st.session_state.language}")
            st.rerun()  # Rerun to switch to chat UI after language selection

        st.stop()

# Part 2: Chat UI (only after language is selected)
# -----------------------
# App Header with Creator Info
# -----------------------
st.markdown(
    """
    <div style="text-align: right; margin-bottom: 1rem;">
        <span style="font-size: 1rem;">Created by: </span>
        <a href="https://www.linkedin.com/in/kuldeepkhatke/" target="_blank" style="font-weight: bold; font-size: 1rem; color: #0077b5; text-decoration: none;">
            Kuldeep Khatke
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)


# st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

user_input = st.chat_input("Say something...")

if user_input:
    if st.session_state.language:
        create_with_message_history(st.session_state.language)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # ---- AI Response (Dummy / Gemma) ----
    with st.spinner("LangCrush is typing..."):
        try:
            bot_reply = with_message_history.invoke(
                [
                    # SystemMessage(content=f"Try to teach sentences around {st.session_state.language} language in hinglish."),
                    HumanMessage(content=user_input)
                ],
                config=config,
            ).content
        except Exception as e:
            bot_reply = f"⚠️ Error: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# -----------------------
# Display chat history
# -----------------------
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
