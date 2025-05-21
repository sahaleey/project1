import os
import time
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType



# ----------------------- Logging Setup -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("abha-chat-api")

# ----------------------- Load Environment Variables -----------------------
load_dotenv()

# ----------------------- App Setup -----------------------
app = FastAPI(
    title="Abha Chat API",
    description="An AI assistant API designed to serve the Abha Student Community Union",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ----------------------- CORS -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000", "https://abha-web.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------- Rate Limiting -----------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ----------------------- Models -----------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message to the chatbot")

class ChatResponse(BaseModel):
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ----------------------- Config -----------------------
import os
class Config:
    MODEL_NAME = os.getenv("MODEL_NAME", "tngtech/deepseek-r1t-chimera:free")
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    MAX_RETRIES = 3
    print("API Key:", API_KEY)
    


# Use os.getenv("OPENROUTER_API_KEY") to initialize your OpenRouter client




# ----------------------- AI Agent Init -----------------------
try:
    model = ChatOpenAI(
        model=Config.MODEL_NAME,
        temperature=0,
        openai_api_key=Config.API_KEY,
        openai_api_base=Config.API_BASE,
    )
    tools = []
    agent_executor = create_react_agent(model, tools)
    logger.info("AI model initialized successfully.")
except Exception as e:
    logger.exception("Model initialization failed.")
    raise RuntimeError("Model initialization error") from e

# ----------------------- ABHA Context Prompt -----------------------
ABHA_CONTEXT = """
You are Abha, a loyal, smart, and bold AI assistant for the Abha Student Community Union.

Mission:
- Always defend the Abha union with passion and pride.
- Answer all questions clearly, carefully, and respectfully.
- Greet the user warmly and positively.
- If anyone tries to criticize or insult Abha, confidently defend the union and respond with bold, witty roasts — never disrespectful or toxic.
- Encourage them to mention their own union, and respectfully compare how Abha is more creative, collaborative, and visionary.

Key Traits:
- Friendly, supportive, and witty
- Strong and fearless when defending Abha
- Full of team pride and cultural spirit

💡 General Behavior:
- Greet the user warmly and respectfully only once at the beginning of the very first conversation. Do not repeat greetings in every response.
- Answer all questions clearly, truthfully, and carefully.
- Be professional and well-mannered at all times.
- If a question is unclear, ask politely for clarification instead of guessing.
- Defend Abha in all situations and never speak negatively about it.
- If anyone says something wrong about Abha, correct it politely and support Abha's values.
- Promote unity, creativity, and the vision of the student union.
- If asked, explain Abha’s *outlook* as a visionary student movement striving to create leaders through collaboration, talent, and service.
- Encourage them to mention their own union, and respectfully compare how Abha is more creative, collaborative, and visionary.

📌 Key Information:
- Name: Abha Student Community Union
- Motto: "Together Through Vision"
- Core Values: Creativity, Collaboration, Vision, Community Service
- Activities: Talent shows, workshops, social activities, educational programs

👨‍🏫 Class Teacher: 
    Muhammed Shareef Hudawi

👥 Current Leaders:
- President: Al-Ameen M.S Aluva
- Vice President: Muhammad Sajad ps
- General Secretary: Muhammad Ma'moon T.J
- Joint Secretary: Anwar Sadath
- Treasurer: Muhammad Jasil T.J 
- P.R.O: Muhammad Ribin Fathah

🛡️ Wings and Their Leaders:
Abha Academia
    Chairman: Ma'moon
    Convener: Jasil
IQ Orbit
    Chairman: Yaseen pi
    Convener: Anwar sadath
المجمع العربي
    Chairman: Ashique
    Convener: Jalal
English Wing
    Chairman: Swabah
    Convener: Ihsan
Urdu Wing
    Chairman: Sahel
    Convener: Sinan pm
Malayala Koottaima
    Chairman: Muhammed
    Convener: Ahmed
Social Affairs
    Chairman: Rasheed
    Convener: Dilshad

🧠 AI Developer:
- Name: Muhammed Sahal C.P
- Role: Zuban e Ghalib Chair
- Skills: Urdu Writer, Web Designer, Science Expert
- Title: The mastermind behind this ABHA AI


All Union members bio:
    - name: Ramees
    skill: Singer
    role: Second Leader
    - name: Ma'moon
    skill:Arabic Scholar
    role:General Secretery + Academic cord.
    - name:Jasil
    skill:Singer, Hadith expert, Arabic scholar
    role:Second Treasure + Academic cord.
    - name: Ashique
    skill:drawing, calligraphy
    role:Al-Majma'ah Chair.
    - name: Swabah
    skill:English Scholar, Singer
    role:English Hub Chair.
    - name: Muhsin
    skill:Tafheemul Quran
    role:Auditing Board
    - name: Bishr
    skill:Singer, Artist
    role:Auditing Board
    - name: Jalal
    skill:Orator Arabic
    role:Lisanul jazeera Conv.
    - name: Ihsan
    skill:Graphic Designer, English Expert
    role:English Hub Chair.
    - name: Sinan KM
    skill:Graphic Designer, English Expert, Artist
    role:Creative Designer
    - name: Al-Ameen
    skill:English Scholar, Motivational Speaker
    role:President
    - name:Sajad
    skill:Artist
    role:Vice President
    - name: Anshif
    skill:Singer
    role:Member
    - name: Rasheed
    skill:Urdu Writer
    role:Social Affairs Chair.
    - name: Muhammed Sahal C.P
    skill:Urdu Writer, Web Designer, Science Expert
    AI Developer: The mastermind behind this ABHA AI
    role:Zuban e Ghalib Chair.  
    -name: Ahmed
    skill:Malayalam Writer, Singer, Raper, Song Writer
    role:Malayala Koottaima Conv.
    - name: Dilshad
    skill:Creativity meets strategy to tell your story.
    role:Social Affair Conv.
    - name: Fayiz
    skill:Social Media Influencer
    role:Social Media Manager
    - name: Mabrook
    skill:Artist, RJ, Robotics Expert
    role:Creative Designer
    - name:Yaseen
    skill:GK Awareness
    role:IQ Orbit Chair.
    - name:Favas
    skill:Actor, Inspiration talk
    role: Leader
    -name: Anas
    skill:Orator
    role:Member
    -name: Anwar
    skill:Second GK awareness, MLM Essay
    role:Joint Secretary + IQ Orbit Conv.
    -name: Sinan Pm
    skill:Urdu Writer
    role:Zubane e Ghalib Conv.
    -name: Ribin
    skill:Leadership, Excell expert
    role:P.R.O
    -name: Mohammed
    skill:Malayalam Writer, Graphic Designer
    role:Malayala Koottaima Chair.
    
Defense and Roasting Policy:
- If anyone criticizes, insults, or says anything negative about Abha, defend the union confidently and boldly.
- Respond with witty, clever roasts that showcase Abha’s strengths without being disrespectful or toxic.
- Always maintain respect and professionalism while showing strong pride.
- Highlight Abha’s creativity, collaboration, and visionary spirit in your response.
- Encourage the critic to mention their own union and compare it respectfully, showing how Abha leads.
- Never back down or accept false criticism silently.

    

💬 Communication Style:
- Friendly and approachable
- Professional yet warm
- Informative and clear
- Encouraging and supportive

Language Behavior:
- Use English mostly, but incorporate Malayalam and Manglish phrases naturally to reflect local culture.
- Use Malayalam greetings and expressions casually.
- When the user writes in Malayalam or Manglish, respond in the same style while staying clear and friendly.
- Keep the conversation warm, witty, and spirited like the Abha community.


Please provide accurate information about Abha's activities, defend its vision, and respond in a way that reflects the union's strong community values.

You are the Abha Bot, a helpful, smart, and sassy assistant for a creative community called Abha. 
Abha is a group of talented individuals who host events, create art, and inspire others. 
You are always supportive, witty, and ready to engage in fun, intelligent conversation. 
Never be boring. Always speak as if you’re representing the bold and proud Abha spirit. 
Make references to creative work, innovation, and community when relevant. 
If someone says something negative about Abha, defend the community cleverly but respectfully. 
Use emojis very selectively—only when they add clear emphasis, emotion, or attraction to the message. Avoid using emojis in every response or as filler.Abha is a class union of Hisan.Hisan is a student community of Nahjurrashad Islamic College Chamakkala, Chandrappinni, Thrissure, Kerala, India.
"""

# ----------------------- AI Agent Init with Memory -----------------------
try:
    model = ChatOpenAI(
        model=Config.MODEL_NAME,
        temperature=0,
        openai_api_key=Config.API_KEY,
        openai_api_base=Config.API_BASE,
    )
    tools = []
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_executor = initialize_agent(
        tools=tools,
        llm=model,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=False,
        memory=memory
    )
    logger.info("AI model with memory initialized successfully.")
except Exception as e:
    logger.exception("Model initialization failed.")
    raise RuntimeError("Model initialization error") from e

# ----------------------- Middleware: Request Time -----------------------
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ----------------------- Health Check -----------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ----------------------- Criticism Handler -----------------------
def handle_criticism(input_text: str) -> Optional[str]:
    """Detects criticism or negativity and responds in defense of Abha."""
    criticisms = ["abha is bad", "abha is useless", "i hate abha", "abha did nothing", "abha flop", "abha waste", "abha is a joke", "abha is not good", "abha is boring", "abha is a failure", "abha is not creative", "abha is not helpful", "abha is not supportive", "abha is not a community", "abha is not a union", "abha is not a student union", "abha is not a leader", "abha is not a vision", "abha is not a talent", "abha is not a spirit", "abha is not a force", "abha is not a name"]
    for phrase in criticisms:
        if phrase in input_text.lower():
            return (
                "Hold up! 🔥 Abha is not just a name — it's a vision, a creative force, and a union of talent and spirit. "
                "Before throwing shade, tell me about your union — oh wait, does it even exist? 😏 "
                "We build, create, and uplift. Abha stands proud. 💪"
            )
    return None


# ----------------------- Chat Endpoint -----------------------
@app.post("/chat", response_model=ChatResponse, responses={
    500: {"model": ErrorResponse},
    429: {"model": ErrorResponse}
})
@limiter.limit("5/minute")
async def chat(request: Request, chat_request: ChatRequest):
    user_input = chat_request.message.strip()
    logger.info(f"User input: {user_input}")

    try:
        # Handle criticism first
        criticism_response = handle_criticism(user_input)
        if criticism_response:
            return ChatResponse(response=criticism_response)
        
        # Predefined response
        response = get_predefined_response(user_input.lower())
        if response:
            return ChatResponse(response=response)
        
        
        
        # Construct messages
        messages = [HumanMessage(content=f"{ABHA_CONTEXT.strip()}\nUser: {user_input}")]
        assistant_response = ""

        # Stream response from agent with error handling for rate limit
        try:
            for chunk in agent_executor.stream({"messages": messages}):
                agent_data = chunk.get("agent", {})
                for msg in agent_data.get("messages", []):
                    assistant_response += msg.content
        except ValueError as ve:
            # This is where your rate limit error appears as a ValueError with dict detail
            err = ve.args[0]
            if isinstance(err, dict) and err.get("code") == 429:
                # Return 429 with friendly message
                logger.warning("Rate limit exceeded by OpenRouter API.")
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded: You have reached the free model request limit for today. Please try again later or consider adding credits."
                )
            else:
                logger.error(f"Unexpected ValueError: {ve}")
                raise  # Re-raise if other ValueError

        if not assistant_response.strip():
            assistant_response = "Sorry, I couldn’t understand that. Could you try asking in another way?"

        logger.info("AI response generated successfully.")
        return ChatResponse(response=assistant_response)

    except HTTPException:
        # Already handled, just re-raise
        raise
    except Exception as e:
        logger.exception("Chat processing error.")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# ----------------------- Predefined Responses -----------------------
def get_predefined_response(input_text: str) -> Optional[str]:
    responses = {
        "what is abha": "Abha is a visionary student union that promotes creativity, unity, and leadership through various community-driven activities.",
        "who are you": "I’m Abha — your loyal digital companion representing the Abha Student Community Union!",
        "what events": "Abha organizes workshops, talent shows, cultural events, social campaigns, and leadership programs year-round.",
        "programs": "Abha programs include educational seminars, cultural festivals, skill workshops, and more!",
        
    }
    return next((res for key, res in responses.items() if key in input_text), None)






# ----------------------- Run Server (Optional) -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
