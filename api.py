from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AzureOpenAI(
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("API_ENDPOINT"),
    api_key=os.getenv("API_KEY"),
)

def get_response(context: str, prompt: str) -> str:

    response = client.chat.completions.create(

        messages=[

            {"role": "system",
             "content": "Eres un asistente muy dinamico y divertido para la \n"
             "Fundación Comunidad DOJO"},

             {"role":"user",
              "content": context + prompt }
        ],
        max_tokens=300,
        temperature=0.5,
        top_p=1,
        model="DEPLOYMENT",
        stream=True, #pal coqueteo
    )

    def generator():
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content or ""
         
    return generator