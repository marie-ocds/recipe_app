import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import SimpleJsonOutputParser
import os
from langchain_groq import ChatGroq
from urllib.parse import quote
import requests


def display_recipe_image(recipe_name):
    api_key = os.getenv('PIXABAY_API_KEY')
    if not api_key:
        print("API key not found.")

    # request
    query = quote(recipe_name)

    # PIXABAY API
    url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&category=food&per_page=5&safesearch=true"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['totalHits'] > 0:
                # URL from first image
                image_url = data['hits'][0]['webformatURL']
                st.image(image_url, caption=recipe_name, use_container_width=True)
            else:
                st.warning(f"No image found for {recipe_name}")
        else:
            st.error(f"Error in API request: {response.status_code}")
    except Exception as e:
        st.error(f"Error while retrieving the image: {e}")

# st.title('Recipes')

txt = st.text_input(label="What do you want to cook?")

model_name = 'gemma2-9b-it'
model = ChatGroq(model = model_name,
                 api_key=os.getenv('GROQ_API_KEY'),
                 temperature=0.5)

temp_class = SimpleJsonOutputParser()


#%% model
system_prompt = """You are a recipe assistant. 
You are given the name of a dish and you have to return the recipe name, 
ingredients and steps in JSON format following this template : 
{{"recipe_name": "...", "ingredients": [{{"name". "...", "quantity": ...}}], "steps": []}}'."""
user_prompt = "Find the ingredients and steps for cooking {input}"


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", user_prompt),
])

user_input = {"input": txt}

# chain
chain = prompt | model | temp_class

if st.button("Find recipe"):
    # output
    recipe = chain.invoke(user_input)
    # render json content with streamlit elements
    st.title(f"{recipe['recipe_name']}")

    # Display image
    display_recipe_image(recipe['recipe_name'])

    # Ingredients
    st.subheader("💫 Ingredients")
    for ingredient in recipe["ingredients"]:
        st.markdown(f"- **{ingredient['name']}**: {ingredient['quantity']}")

    # Steps
    st.subheader("📝 Steps")
    for i, step in enumerate(recipe["steps"], start=1):
        st.markdown(f"{i}. {step.capitalize()}")

    # Footer
    st.markdown("---")
    st.caption("Lass euch schmecken! 🌟")

