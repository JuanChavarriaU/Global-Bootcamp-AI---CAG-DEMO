from openai import AzureOpenAI
from dotenv import load_dotenv
from datetime import datetime
from dateutil import tz
import os
import hashlib
import json

load_dotenv()

# Directorio para almacenar el cache
CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

client = AzureOpenAI(
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("API_ENDPOINT"),
    api_key=os.getenv("API_KEY"),
)

def get_response(query: str, knowledge_file: str) -> str:
    """
    Params:
    Query: str
    Knowledge file: str

    Consulta la API de OpenAI usando Cache-Augmented Generation.
    Se carga el conocimiento desde un archivo, se genera la clave del cache y se devuelve la respuesta,
    ya sea desde cache o mediante la llamada a la API.
    """
    try:
        # Cargar el conocimiento pre-cargado desde el archivo
        knowledge_cache = load_knowledge_cache(knowledge_file)
    except Exception as e:
        return lambda: fake_stream_from_cache("No se pudo cargar el conocimiento")
    # Generar la clave única de cache a partir del conocimiento y la consulta
    cache_key = get_cache_key(knowledge_cache, query)
    cached = get_cached_response(cache_key)

    if cached:
        print("✅ Respuesta obtenida desde el cache")
        return lambda: fake_stream_from_cache(cached)

    prompt = f"""
    Contexto: 
    {knowledge_cache}
    
    Consulta: 
    {query}

    Respuesta:
    """

    return openai_call(prompt=prompt, cache_key=cache_key) 
        
    
         
def openai_call(prompt: str, cache_key: hashlib) -> str:

    response = client.chat.completions.create(

            messages=[
                    {"role": "system", "content": "Eres un asistente muy útil para la Fundación Comunidad DOJO."},
                    {"role": "user", "content": prompt}
                ],
            max_tokens=4096,
            temperature=0.5,
            top_p=1,
            model="DEPLOYMENT",
            stream=True, #pal coqueteo
        )
    
    def generator():
        answer = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                answer += content
                yield content
        cache_response(cache_key, answer)

    return generator

def fake_stream_from_cache(text: str, chunk_size: int = 10):
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]



def cache_response(cache_key: str, answer: str):
    """
    Guarda la respuesta en un archivo JSON.
    Se almacena un timestamp para futuras mejoras (por ejemplo, implementar TTL).
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    data = {
        "timestamp": datetime.now(tz.UTC).isoformat(),
        "answer": answer
    }
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error al guardar el cache: {e}")


def load_knowledge_cache(file_path: str) -> str:
    """
    Lee el contenido del archivo TXT que contiene el conocimiento pre-cargado.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error al leer el archivo de conocimiento: {e}")
        return ""        
    
def get_cache_key(context: str, query: str) -> str:
    """
    Genera una clave única a partir del contexto y la consulta.
    """
    combined = f"{context.strip()}|{query.strip()}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()    

def get_cached_response(cache_key: str) -> str:
    """
    Intenta recuperar la respuesta cacheada desde un archivo JSON.
    Devuelve None si no existe o falla la lectura.
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("answer")
        except Exception as e:
            print(f"Error al leer el cache: {e}")
    return None