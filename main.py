from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Flutter'dan (veya ileride webden) gelecek isteklere tamamen kapıyı açan güvenlik kilidi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key=api_key)

# 1. Flutter'dan gelen JSON verisini karşılayacak modeli tanımlıyoruz
class ImageRequest(BaseModel):
    image: str

@app.get("/")
def home():
    return {"message": "API Çalışıyor!"}

# 2. Adını Flutter ile aynı yaptık (/solve) ve JSON formatını kabul etmesini sağladık
@app.post("/solve")
async def solve_math_problem(request: ImageRequest):
    
    # Flutter zaten fotoğrafı Base64'e çevirip gönderdiği için direkt alıyoruz
    base64_image = request.image
   
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Eğer daha zorlu integral/türev sorularında zorlanırsa "gpt-4o" modeline geçebilirsin.
            messages=[
                {
                    "role": "system",
                    "content": "Sen matematik sorularını çözme konusunda uzman bir asistansın. Sana verilen fotoğraftan soruyu analiz et, adım adım çöz ve anlaşılabilir bir şekilde anlat. Formülleri belirgin bir şekilde yaz."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Lütfen bu fotoğraftaki matematik sorusunu çöz."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1500,
        )
        
        description = response.choices[0].message.content
        return {"description": description}
    
    except Exception as e:
        return {"error": str(e)}