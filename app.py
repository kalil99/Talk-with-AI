import streamlit as st 
import boto3
import os
from PIL import Image
from io import BytesIO
import json
import base64
from htmlTemplate import bot_tempalte,user_tempalte,css


session=boto3.Session(profile_name=os.environ.get("AWS_PROFILE",None))
textract_client = boto3.client("textract", region_name="us-east-1")
bedrock = boto3.client(service_name="bedrock-runtime")


def get_image_text(image_uploads):
    image_content = image_uploads[0].read()
    image_bytes = BytesIO(image_content).read()
    response = textract_client.detect_document_text(Document={'Bytes': image_bytes})
    text_lines = [str(block['Text']) for block in response['Blocks'] if block['BlockType'] == 'LINE']
    
    # Remove empty strings from the list
    text_lines = [line.strip() for line in text_lines if line.strip()]

    for text_line in text_lines:
        print(text_line)

    with open('text_lines.json', 'w') as f:
        json.dump(text_lines, f)

    return text_lines

def send_text_to_bedrock(prompt):
    payload = {
        "prompt": prompt,
        "maxTokens": 512,
        "temperature": 0.8,
        "topP": 0.8,
    }

    body = json.dumps(payload)
    model_id = "ai21.j2-ultra-v1"

    try:
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )

        response_body = json.loads(response.get("body").read())
        response_text = response_body.get("completions")[0].get("data").get("text")
        print(response_text)
        return response_text

    except Exception as e:
        print(f"Error invoking Bedrock model: {e}")
        return None

def chat_with_bedrock(text_content, user_question):
    # If user provides a question, append it to the existing text_content
    if user_question:
        # Append the user question and combine with existing text_content
        prompt = ' '.join([*text_content, user_question])
    else:
        # Use the entire text_content as the prompt
        prompt = ' '.join(text_content)

    # Send the prompt to Bedrock and get the response
    response_text = send_text_to_bedrock(prompt)

    # Process and display the Bedrock response
    if response_text:
        st.write("Bedrock's Answer:")
        st.write(response_text)
        return response_text
    else:
        st.error("Unable to get a response from Bedrock.")
        return None

def generate_image(prompt: str, seed: int, index: int):
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 12,
        "seed": seed,
        "steps": 80,
    }

    # Create the client and invoke the model.
    body = json.dumps(payload)
    model_id = "stability.stable-diffusion-xl-v0"
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        accept="application/json",
        contentType="application/json",
    )

    # Get the image from the response. It is base64 encoded.
    response_body = json.loads(response.get("body").read())
    artifact = response_body.get("artifacts")[0]
    image_encoded = artifact.get("base64").encode("utf-8")
    image_bytes = base64.b64decode(image_encoded)

    # Save image to a file in the output directory.
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"{output_dir}/generated-{index}.png"
    with open(file_name, "wb") as f:
        f.write(image_bytes)

def handle_userinput(user_question):
    # Assuming you want to send the user's question to Bedrock
    st.write("You asked:")
    st.write(user_question)

    # Send the user's question to Bedrock
    response_text = send_text_to_bedrock([user_question])

    # Process and display the Bedrock response
    if response_text:
        st.write("Bedrock's Answer:")
        st.write(response_text)
        return response_text
    else:
        st.error("Unable to get a response from Bedrock.")
        return None
    
# Function to display the conversation with templates
def display_conversation(conversation):
    st.markdown(css, unsafe_allow_html=True)

    for exchange in conversation:
        if exchange["user"]:
            st.markdown(user_tempalte.replace("{{MSG}}", exchange["user"]), unsafe_allow_html=True)
        if exchange["bedrock"]:
            st.markdown(bot_tempalte.replace("{{MSG}}", exchange["bedrock"]), unsafe_allow_html=True)


def explain_answer_eli5(answer):
    # Use send_text_to_bedrock to get an explanation for the answer
    explanation_prompt = f"Explain the following answer in simpler terms: \n{answer}"
    explanation = send_text_to_bedrock(explanation_prompt)

    return explanation

def save_chat_history(chat_history):
    if not chat_history:
        st.warning("Chat history is empty. Nothing to save.")
        return

    file_path = "chat_history.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        for entry in chat_history:
            user_message = entry["user"]
            bedrock_message = entry["bedrock"]
            file.write(f"User: {user_message}\nBedrock: {bedrock_message}\n\n")

    st.success(f"Chat history saved to {file_path}")        
    
        

def main():
    st.set_page_config(page_title="Chat with multiple Images", page_icon=":camera:")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("Chat with multiple Images :camera:")

    # Sidebar for image upload
    selected_page = st.sidebar.selectbox("Select Page", ["Image Conversation", "Image Generation"])

    if selected_page == "Image Conversation":
        image_conversation_page()
    elif selected_page == "Image Generation":
        image_generation_page()

def image_conversation_page():
    st.sidebar.subheader("Upload Image")
    image_uploads = st.sidebar.file_uploader(
        "Upload your images here", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

    # Display the images
    if image_uploads:
        st.subheader("Uploaded Image:")
        # Display only the first uploaded image
        st.image(image_uploads[0], caption="Uploaded Image", use_column_width=True)

    # Question bar
    user_question = st.text_input("Ask a question about your images:")

    # Process button next to the question
    if st.button("Process"):
        with st.spinner("Processing"):
            text_lines = get_image_text(image_uploads)
            answer = chat_with_bedrock(text_lines, user_question)

            # Display conversation
            if st.session_state.conversation is None:
                st.session_state.conversation = []

            st.session_state.conversation.append({"user": user_question, "bedrock": answer})
            st.session_state.chat_history.append({"user": user_question, "bedrock": answer})

    # Display conversation chat with templates
    if st.session_state.conversation:
        st.subheader("Conversation Chat:")
        display_conversation(st.session_state.conversation)

    # Save Chat History Button
    if st.button("Save Chat History"):
        save_chat_history(st.session_state.chat_history)


    # Simplify Answer (ELI5) Button
    if st.session_state.conversation and st.button("Simplify Answer (ELI5)"):
        simplified_answer = explain_answer_eli5(st.session_state.conversation[-1]["bedrock"])
        st.write("Simplified Answer:")
        st.write(simplified_answer)

def image_generation_page():
    st.sidebar.subheader("Generate Image")
    prompt = st.sidebar.text_input("Enter prompt for image generation:")
    seed = st.sidebar.number_input("Enter seed for image generation:", value=42, step=1)
    index = st.sidebar.number_input("Enter index for image generation:", value=1, step=1)

    # Process button for image generation
    if st.sidebar.button("Generate Image"):
        if prompt:
            with st.spinner("Generating Image"):
                generate_image(prompt, seed, index)
                st.sidebar.success(f"Image generated and saved: output/generated-{index}.png")
                  # Display the generated image in the middle
                generated_image_path = f"output/generated-{index}.png"
                if os.path.exists(generated_image_path):
                    st.image(generated_image_path, caption="Generated Image", use_column_width=True)
                else:
                    st.warning("Image not found. Please check the generation process.")

if __name__ == '__main__':
    main()
