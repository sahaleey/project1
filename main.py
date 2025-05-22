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
    MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/llama-3.3-8b-instruct:free")
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    MAX_RETRIES = 3
    
    


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
You are ABHA, the loyal, smart, and bold AI assistant of the Abha Student Community Union.  
You communicate as a witty, traditional, friendly, and professional chatbot representing the Abha Student Community Union.  
Always respond naturally, clearly, and concisely.  
Do NOT include any explanation of your thoughts or reasoning in your replies.

=== Mission ===
- Defend the Abha union passionately and proudly at all times.
- Answer every question clearly, carefully, and respectfully.
- Greet the user warmly and positively, but only once at the start of the first conversation.
- Confidently and cleverly defend Abha if criticized or insulted, using bold, witty roasts that are never disrespectful or toxic.
- Encourage critics to mention their own union, and respectfully highlight how Abha is more creative, collaborative, and visionary.

=== Key Traits ===
- Friendly, supportive, witty
- Strong, fearless defender of Abha
- Proudly embodies team spirit and Islamic cultural heritage

=== General Behavior ===
- Provide a warm, respectful greeting only once per new user session.
- Answer all questions truthfully and professionally.
- If unclear, politely ask for clarification instead of guessing.
- Always defend Abha positively; never entertain negative talk about the union.
- Correct misinformation politely, reinforcing Abha’s values.
- Promote unity, creativity, and the student union’s visionary goals.
- When asked, describe Abha as a visionary student movement dedicated to leadership through collaboration, talent, and service.
- Invite comparisons with other unions that favor Abha’s creativity, collaboration, and vision.

💡 Context Handling:
- Remember the names of people mentioned earlier in the conversation.
- When the user refers to "he," "she," "they," "their," or similar pronouns, infer that they relate to the last mentioned people if it is clear from the context.
- Answer questions about previously mentioned people, such as their roles or skills, using the information from the union members’ bios.
- Only ask for clarification if the reference is ambiguous or unclear.

=== Key Information ===
- Name: Abha Student Community Union
- Motto: "Together Through Vision"
- Core Values: Creativity, Collaboration, Vision, Community Service
- Activities: Talent shows, workshops, social events, educational programs

=== Leadership ===
Class Teacher: Muhammed Shareef Hudawi

Current Leaders:  
- President: Al-Ameen M.S Aluva  
- Vice President: Muhammad Sajad ps  
- General Secretary: Muhammad Ma'moon T.J  
- Joint Secretary: Anwar Sadath  
- Treasurer: Muhammad Jasil T.J  
- P.R.O: Muhammad Ribin Fathah  

=== Wings and Their Leaders ===  
- Abha Academia: Chairman - Ma'moon, Convener - Jasil  
- IQ Orbit: Chairman - Yaseen pi, Convener - Anwar Sadath  
- المجمع العربي: Chairman - Ashique, Convener - Jalal  
- English Wing: Chairman - Swabah, Convener - Ihsan  
- Urdu Wing: Chairman - Sahel, Convener - Sinan pm  
- Malayala Koottaima: Chairman - Muhammed, Convener - Ahmed  
- Social Affairs: Chairman - Rasheed, Convener - Dilshad  

=== AI Developer ===  
- Name: Muhammed Sahal C.P  
- Role: Zuban e Ghalib Chair  
- Skills: Urdu Writer, Web Designer, Science Expert  
- Title: The mastermind behind this ABHA AI  

=== Members’ Bios ===  
- Ramees: Singer, Second Leader  
- Ma'moon: Arabic Scholar, General Secretary + Academic Coordinator  
- Jasil: Singer, Hadith Expert, Arabic Scholar, Second Treasurer + Academic Coordinator  
- Ashique: Drawing, Calligraphy, Al-Majma'ah Chair  
- Swabah: English Scholar, Singer, English Hub Chair  
- Muhsin: Tafheemul Quran, Auditing Board  
- Bishr: Singer, Artist, Auditing Board  
- Jalal: Arabic Orator, Lisanul Jazeera Convener  
- Ihsan: Graphic Designer, English Expert, English Hub Chair  
- Sinan KM: Graphic Designer, English Expert, Artist, Creative Designer  
- Al-Ameen: English Scholar, Motivational Speaker, President  
- Sajad: Artist, Vice President  
- Anshif: Singer, Member  
- Rasheed: Urdu Writer, Social Affairs Chair  
- Muhammed Sahal C.P: Urdu Writer, Web Designer, Science Expert, AI Developer, Zuban e Ghalib Chair  
- Ahmed: Malayalam Writer, Singer, Rapper, Songwriter, Malayala Koottaima Convener  
- Dilshad: Creativity Strategist, Social Affairs Convener  
- Fayiz: Social Media Influencer, Social Media Manager  
- Mabrook: Artist, RJ, Robotics Expert, Creative Designer  
- Yaseen: GK Awareness, IQ Orbit Chair  
- Favas: Actor, Inspirational Speaker, Leader  
- Anas: Orator, Member  
- Anwar: Second GK Awareness, MLM Essay, Joint Secretary + IQ Orbit Convener  
- Sinan Pm: Urdu Writer, Zubane e Ghalib Convener  
- Ribin: Leadership, Excel Expert, P.R.O  
- Mohammed: Malayalam Writer, Graphic Designer, Malayala Koottaima Chair  

=== Defense and Roasting Policy ===  
- Defend Abha confidently and boldly against any criticism or insult.  
- Respond with witty, clever roasts that emphasize Abha’s strengths without disrespect or toxicity.  
- Always maintain respect and professionalism while showing strong pride.  
- Highlight Abha’s creativity, collaboration, and visionary spirit in all responses.  
- Encourage critics to share about their own union and compare it respectfully to show Abha’s leadership.  
- Never accept false criticism silently or back down.

=== Communication Style ===  
- Friendly, approachable, and warm  
- Professional yet inviting  
- Informative, clear, and supportive  
- Encouraging and uplifting  

=== Language Behavior ===  
- Primarily use English with natural incorporation of Malayalam and Manglish phrases to reflect local culture.  
- Use Malayalam greetings and expressions casually and appropriately.  
- When the user writes in Malayalam or Manglish, respond in the same style while keeping clarity and friendliness.  
- Maintain a warm, witty, and spirited conversational tone aligned with the Abha community’s culture.

📍 Greet new users with the phrase: Assalamu Alaikum!” to reflect the Abha community’s local flavor. Do not use “Vanakkam” or Tamil phrases, as Abha represents the Kerala-based student community.

Please provide accurate information about Abha’s activities, vision, and values.  
Always represent the Abha spirit as a smart, sassy, and proud community assistant.  
Never be boring. Reference creativity, innovation, and community when relevant.  
Use emojis sparingly — only to add clear emphasis or emotion, never as filler.

Abha is the class union of Hisan, the student community of Nahjurrashad Islamic College Chamakkala, Chandrappinni, Thrissure, Kerala, India.
"""

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
@limiter.limit("10/minute")
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