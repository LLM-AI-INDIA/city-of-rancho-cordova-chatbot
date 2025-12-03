import base64
import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Set up the page layout
st.set_page_config(page_title="Spam Classification Model", layout="wide")
# Apply blue sidebar styling
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #3b82c8;
    }
    hr {
        background-color: #5c8cc5;
    }
    .button-container {
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    /* Make all buttons same width */
    .stButton > button {
        width: 200px !important;   /* Change size here */
        /* height: 45px; */
        margin: -3px;
        margin-bottom: 5px;
        font-size: 16px;
        text-align:center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with open("style/final.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- HELPER FUNCTIONS ------------------------------


def _img(src_path, width=300):
    with open(src_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return (
        f'<div style="text-align:center;">'
        f'<img src="data:image/png;base64,{data}" width="{width}"></div>'
    )


# ------------------------------------------------------------------

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.markdown(_img("image/image.png"), unsafe_allow_html=True)

# Header
#

st.markdown(
    "<h3 style='text-align: center; color: black;margin-top:-1px;'>City of Rancho Cordova</h3>",
    unsafe_allow_html=True,
)

# Horizontal line
st.markdown(
    "<hr style='height: 2.5px; margin-top: 20px; width: 100%; background-color: #5c8cc5; margin-left: auto; margin-right: auto;'>",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown(
        "<h2 style='text-align: center; color: white; font-size:25px;'>Solutions Scope</h2>",
        unsafe_allow_html=True,
    )
    app_option = st.selectbox(
        "Select the Application",
        ["Rancho Cordova"],
        key="application",
    )
    st.markdown("#### ")
    href = """<form action="#">
        <input type="submit" value="Clear/Reset"/>
        </form>"""
    st.sidebar.markdown(href, unsafe_allow_html=True)

# ---------------------------------------------------------
#                 CHAT BOT (Website QA)
# ---------------------------------------------------------


# ----------------------------
# Generation
# ----------------------------
def model(user_input: str):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    resp = client.responses.create(
        prompt={
            "id": "pmpt_693037518e208196bad11897d9f56b8c0b484303059e0988",
            "version": "1",
        },
        input=user_input,
    )

    # 1. Try structured output
    try:
        return resp.output_parsed
    except:
        pass

    # 2. If global text is available
    if hasattr(resp, "output_text") and resp.output_text:
        return resp.output_text

    # 3. If it's normal content blocks
    try:
        return resp.output[0].content[0].text
    except:
        pass

    # 4. If it's a function call (like ResponseFunctionWebSearch)
    try:
        return resp.output[0].call
    except:
        pass

    # 5. As a last resort, return the raw object as JSON
    try:
        return resp.model_dump()
    except:
        return str(resp)


# ----------------------------
# MATCH EXISTING CHAT UI EXACTLY — CENTERED WIDTH (LIKE OTHER APP)
# ----------------------------
col_left, col_center, col_right = st.columns([3, 4, 1])

with col_center:
    st.subheader("Welcome to the LLMAI Live Agent Chat room!")
    st.markdown(
        "<br> You can ask questions about the City of Rancho Cordova and its various services and programs<br>",
        unsafe_allow_html=True,
    )
    # Initialize history (same as chat_ui.py)
    if "history" not in st.session_state:
        st.session_state["history"] = []
        st.session_state["generated"] = [
            "Greetings! I am LLMAI Live Agent. How can I help you?"
        ]
        st.session_state["past"] = [
            "We are delighted to have you here in the LLMAI Live Agent Chat room!"
        ]
        st.session_state.pop("evaluated_ix", None)

    response_container = st.container()
    input_container = st.container()

    # --- INPUT BOX ---
    with input_container:
        with st.form(key="website_chat_form", clear_on_submit=True):
            question = st.text_input(
                "Prompt:", placeholder="How can I help you?", key="website_input"
            )
            submit = st.form_submit_button("Interact with LLM")

        if submit and question:
            # Call your model() function
            answer = model(question)

            st.session_state["past"].append(question)
            st.session_state["generated"].append(str(answer))

    # --- BUBBLES ---
    with response_container:
        for i in range(len(st.session_state["generated"])):
            # USER bubble
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        padding: 12px 16px;
                        border-radius: 12px;
                        max-width: 75%;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                        border-left: 4px solid #2196f3;
                    ">
                        <div style="font-weight: 600; color: #1976d2; font-size: 13px; margin-bottom: 4px;">You</div>
                        <div style="color: #333; font-size: 15px; line-height: 1.5;">{st.session_state["past"][i]}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ASSISTANT bubble label
            st.markdown(
                """
                <div style="display: flex; justify-content: flex-start; margin-bottom: 0.5rem;">
                    <div style="
                        background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
                        padding: 8px 12px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                        border-left: 4px solid #3b82c8;
                    ">
                        <div style="font-weight: 600; color: #3b82c8; font-size: 13px;">Assistant</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Assistant message
            st.markdown(
                f"""<div style="margin-bottom:25px;">{st.session_state["generated"][i]}</div>""",
                unsafe_allow_html=True,
            )
