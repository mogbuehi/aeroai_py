import streamlit as st
from openai import OpenAI
import os

def create_assistant():
  # Define the path to your text file
  file_path = 'instructions.txt'

  # Use the with statement to open the file
  with open(file_path, 'r') as file:
      # Read the content of the file
      instructions = file.read()
  
  # OpenAI Assistant API endpoint
  assistant = client.beta.assistants.create(
    name="CBTA Assistant",
    instructions=instructions,
    tools=[{"type": "retrieval"}],
    model="gpt-3.5-turbo-preview",
  )

# Function to upload files and return a mapping of file names to OpenAI IDs
def upload_files(folder_path):
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for file_path in file_paths:
        with open(file_path, "rb") as file:
            assistant_file = client.beta.assistants.files.create(
                assistant_id=assistant_id,
                file_id=os.path.basename(file_path)
                )

            print(f"Uploaded {file_name} with ID: {file_id}")
    
    return file_ids

# Streamlit UI for folder input and file upload
st.title('Upload Files to OpenAI')

folder_path = st.text_input('Enter the folder path containing files to upload:', '')

if st.button('Upload Files'):
    if folder_path:
        file_ids = upload_files(folder_path)
        if file_ids:
            st.success(f'Successfully uploaded {len(file_ids)} files.')
            for file_name, file_id in file_ids.items():
                st.write(f"{file_name}: {file_id}")
        else:
            st.warning('No files found to upload.')
    else:
        st.error('Please enter a valid folder path.')

