import streamlit as st
from trainer import ai_assistant, pdf_agent
# from ppt_gen import convert_pptx_to_images
from dotenv import load_dotenv, find_dotenv
# from pptx import Presentation
import os
from openai import OpenAI

# Initialize session state for the input field if not already set
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

# Initiate client and save api_key to state
if 'api_key' not in st.session_state:
    load_dotenv(find_dotenv())
    api_key = os.getenv('OPENAI_API_KEY')
    st.session_state.api_key = api_key

api_key = st.session_state.api_key
client = OpenAI(api_key=api_key)

# Setting up other state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id
thread_id = st.session_state['thread_id']

if 'pdf_thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state['ppt_thread_id'] = thread.id
pdf_thread_id = st.session_state['thread_id']


## Tab for Chat and Presentation
pdf_tab, chat_tab = st.tabs(['🎓 Presentation', '💬 Chat'])

with chat_tab:
    # Initialize session state for messages and thread_id if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if 'thread_id' not in st.session_state:
        thread = client.beta.threads.create() 
        st.session_state['thread_id'] = thread.id

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message['content'])


    # Chat input
    user_input = st.chat_input('Type your query here and hit enter')

    # Handle the chat interaction
    if user_input:  # Check if there is an input to send
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(user_input)

        # Assume ai_assistant is a function that sends the message to the OpenAI API and gets a response
        text_response = ai_assistant(user_input=user_input, thread_id=st.session_state.thread_id, client=client)
        assistant_message = {"role": "assistant", "content": text_response}
        assistant_response = st.chat_message(name=assistant_message['role'])
        assistant_response.markdown(text_response)
        st.session_state.messages.append(assistant_message)
        
        # Create audio response
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=assistant_message['content']
            )        
        
        audio_response.stream_to_file('audio.mp3')
        
        pdf_agent(convo_input=f'''**Student**: {user_input}
                  **CBTA Assistant**: {text_response}''', thread_id=pdf_thread_id,
                  client=client)
        
        # audio_response.with_streaming_response.method('audio.mp3')


# Presentation Tab-----------------------------------
with pdf_tab:
    import base64

    def show_pdf(file_path):
        with open(file_path, "rb") as file:
            base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="120%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    # Display the PDF
    if os.path.exists('presentation.pdf'):
        show_pdf('presentation.pdf')


# st.write("No slides found in the presentation.")



# Sidebar----------------------------------------------------------------
## AI Avatar Video (PNG video possible?)
with st.sidebar:
    # st.page("app.py", label="Home", icon="🏠")
    # st.page_link("pages/create_assistant.py", label="create assistant")

    st.markdown('Hit play button to hear the assistant')
    # st.video('Assets/video.mp4')
    st.audio('audio.mp3')

    # loading doc into memory ONLY when the button is clicked
    def get_pdf():
        with open("Resources/AreoAI Workflow.pdf", 'rb') as file:
            return file.read()
    
    st.download_button(
        label='Download Slides PDF',
        data=get_pdf(),
        file_name=('presentation.pdf'),
        mime=('application/pptx')

    )
