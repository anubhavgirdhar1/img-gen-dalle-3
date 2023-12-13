import streamlit as st
import os
import json
from openai import OpenAI
from streamlit import secrets
# from streamlit_extras.switch_page_button import switch_page
client = OpenAI(api_key="")

COST_FILE = "costs.json"
IMAGE_COST = 0.04  # USD per image
TEXT_COST_PER_1K_TOKENS = 0.03  # USD for input, 0.06 for output

def read_costs():
    if not os.path.exists(COST_FILE):
        return {"image_cost": 0, "text_cost": 0}
    with open(COST_FILE, "r") as file:
        return json.load(file)

def write_costs(costs):
    with open(COST_FILE, "w") as file:
        json.dump(costs, file)

def update_image_cost():
    costs = read_costs()
    costs["image_cost"] += IMAGE_COST
    write_costs(costs)

def update_text_cost(token_count):
    costs = read_costs()
    costs["text_cost"] += (token_count / 1000) * (TEXT_COST_PER_1K_TOKENS * 2)  # Input + Output cost
    write_costs(costs)

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        quality="standard",
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    update_image_cost()
    return image_url

def generate_contnet(prompt2):
    completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                      {"role": "user", "content": prompt2}]
        )
    generated_output = completion.choices[0].message
    token_count = len(completion.choices[0].message)  # Example token count calculation
    update_text_cost(token_count)   
    return generated_output

def main():

    st.set_page_config(page_title="TrendVerse",page_icon="logo2.png",layout="wide")  # Set the page layout to wide by default
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    costs = read_costs()
    st.sidebar.write(f"Total Image Cost: ${costs['image_cost']:.2f}")
    st.sidebar.write(f"Total Text Cost: ${costs['text_cost']:.2f}")

    image_url = None
    col1, col2 = st.columns(2)
    with col1:
        st.header("DALLE-3 Access")
        prompt = st.text_input("Enter a prompt", "", help="Generate an image of....")
        if col1.button("Generate Content"):
            if prompt.strip():
                image_url = generate_image(f"Take the following prompt and generate an image: {prompt}")
                col2.header("Generated Iamge")
                col2.image(image_url, caption='Generated Image', use_column_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.header("GPT4 Access")
        prompt2 = st.text_input("Enter a prompt", "Key1", help="Generate an image of....")
        if col5.button("Generate output"):
            if prompt2.strip():
                generated_output = generate_contnet(f"You are a smart assistant named Shri, here is the prompt {prompt2}")
                col5.markdown(generated_output)
        

if __name__ == "__main__":
    main()
