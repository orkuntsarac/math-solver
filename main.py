from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


api_key = os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key=api_key)

@app.get("/")
def home():
    return {"message": "NeBu API Çalışıyor!"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
   
    image_data = await file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

   
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

# Çalıştırmak için terminale: uvicorn main:app --reload