import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from datetime import datetime

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
    session_id: str = Field(default="default", description="Session ID to maintain conversation history")

class ChatResponse(BaseModel):
    response: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ----------------------- Config -----------------------
class Config:
    MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-nano-9b-v2:free")
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    MAX_RETRIES = 3
    MAX_HISTORY = 10 
    RATE_LIMIT_DELAY = 1.0  # Number of messages to remember

# ----------------------- Conversation Memory -----------------------
class ConversationMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_session(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        session.append({"role": role, "content": content})
        # Keep only the most recent messages
        if len(session) > Config.MAX_HISTORY * 2:  # *2 because we store both user and AI messages
            self.sessions[session_id] = session[-Config.MAX_HISTORY * 2:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.get_session(session_id)

memory = ConversationMemory()
# ----------------------- ABHA Program -----------------------

abha_programs = [
    {
        "name": "Head start",
        "stage": "7th Class",
        "host": "Rafi Hudawi Muvattupuzha",
        "date": "31/04/2025",
        "time": "4 : 20 PM",
        "description": "Head Start’ marked the energetic launch of our journey, led by Rafi Muvattupuzha. This kickoff event set the tone for our community’s mission, inspiring everyone with motivation, clear direction, and a powerful sense of purpose."
    },
    {
        "name": "ABHA Official inauguration",
        "stage": "7th Class",
        "host": "Usthad Younus Hudawi",
        "date": "31/04/2025",
        "time": "6 : 00 AM",
        "description": "Join us as we mark the official inauguration of our Abha community — a celebration of new beginnings, shared visions, and the exciting journey ahead. Together, we open the doors to creativity, connection, and growth."
    },
    {
        "name": "വിയർപ്പു തുന്നിയിട്ട കുപ്പായം",
        "stage": "Inter lock",
        "host": "Ahmed Zainudheen",
        "date": "01/05/2025",
        "time": "11 : 20 AM",
        "description": "On May 1, led by Ahmed Zainudheen, we celebrated Labour Day, honoring workers’ dedication and the dignity of labour."
    },
    {
        "name": "നേർകാഴ്ച ",
        "stage": "Radio",
        "host": "Yaseen Pi, Anwar",
        "date": "03/05/2025",
        "time": "08 : 15 PM",
        "description": "On May 03, World Press Day. We conducted a live radio to talk about Indian anti-freedom of media"
    },
    {
        "name": "Defend freedom of Press",
        "date": "03/05/2025",
        "description": "World Press Day. Freedom for Press!"
    },
    {
        "name": "നൻ പകൽ നേരത്തെ ജോലി",
        "date": "01/05/2025",
        "description": "World Labour Day Special Poster"
    },
    {
        "name": "ഒന്നും ഒന്നും ഒന്ന്",
        "stage": "Out Campus",
        "host": "ABHA",
        "date": "05/05/2025",
        "time": "06 : 00 AM to 10 : 00 PM",
        "description": "നമ്മൾ ഒത്തു ചേരുമ്പോൾ ആഗ്രഹങ്ങൾക്കു കരുത്തും പ്രവർത്തനങ്ങൾക്ക് ചിറകുകളും പിറക്കുന്നു. നമ്മുടെ ഗ്രൂപ്പ് ശക്തമായി മുന്നേറാൻ, സഹകരണത്തിൻ്റെയും പ്രചോദനത്തിൻ്റെയും ഈ ഘട്ടം ഒരിക്കലുമറക്കരുത്!"
    },
    {
        "name": "Al-Dheenu  Al-Nasweeha",
        "stage": "Out Campus",
        "host": "Usthad Shuaib Hudawi",
        "date": "05/05/2025",
        "time": "In Camp",
        "description": "برنامج «الدين النصيحة» بقيادة الشيخ شعيب هداوي في المسجد، يجمعنا على دروس الإيمان والصدق.\nفرصة للارتقاء بأرواحنا وتزكية قلوبنا بنور النصيحة والمحبة."
    },
    {
        "name": "Let Me Fly",
        "stage": "Out Campus",
        "host": "Usthad Abi Vakkas Usthad",
        "date": "05/05/2025",
        "time": "In Camp",
        "description": "Let Me Fly” with Usthad Vakkas Hudawi — where your dreams grow wings and your skills find their sky.\nIt’s time to rise, break limits, and soar toward the greatness waiting inside you!"
    },
    {
        "name": "Mothers day : Special poster",
        "date": "11/05/2025",
        "description": "Join Abha Community in honoring the unconditional love, strength, and sacrifices of mothers everywhere! Our special Mother’s Day poster is a vibrant tribute to the incredible women who shape our lives with warmth and wisdom."
    },
    {
        "name": "Know The Legend",
        "stage": "7th Class",
        "host": "English Wing",
        "date": "Every Tuesday",
        "description": "Journey into Romanticism! The English Wing's #KnowTheLegend series begins with William Wordsworth – explore the poet who made nature sing. Stay tuned!"
    },
    {
        "name": "Nurse Day : Special Poster",
        "date": "12/05/2025",
        "description": "Saluting Our Angels in Scrubs! This #InternationalNursesDay, Abha celebrates the compassion, courage and tireless care of nurses who heal the world every day. Join us in honoring these healthcare heroes!"
    },
    {
        "name": "Al-Judoor",
        "stage": "7th Class",
        "host": "Ma'moon",
        "date": "01/05/2025",
        "time": "8 : 00 PM",
        "description": "Al-Judoor is an Abha Academia initiative by our union to teach students the foundational grammar of Arabic in an engaging and accessible way."
    },
    {
        "name": "Fluent Flicks",
        "stage": "7th Class",
        "host": "Ihsan",
        "date": "Every Wednesday",
        "time": "8 : 30 PM",
        "description": "Fluent Flicks is an English Wing program designed to introduce students to new English vocabulary through fun and interactive learning."
    },
    {
        "name": "ABHA Parliament - Janashabdam",
        "stage": "7th Class",
        "host": "Class leader",
        "date": "All Month last Week",
        "time": "9 : 30 PM",
        "description": "ABHA Parliament is an inspiring initiative to empower and motivate the class wing through leadership, collaboration, and active participation."
    },
    {
        "name": "Carrier Guidance",
        "stage": "7th Class",
        "host": "Usthad Muhammad Asif Hudawi",
        "date": "15/05/2025",
        "time": "3 : 20 PM",
        "description": "A Career Guidance class by Usthad Muhammed Asif Hudawi is being conducted to help students make informed and purpose-driven career choices."
    },
    {
        "name": "നേര്‍കാഴ്ച - മോദിയോടുള്ള ചോദ്യങ്ങള്‍",
        "stage": "In front of 7th Class",
        "host": "Anwar sadath",
        "date": "13/05/2025",
        "time": "9 : 30 PM",
        "description": "IQ Orbit is hosting a group discussion titled \"നേര്‍കാഴ്ച - മോദിയോടുള്ള ചോദ്യങ്ങള്‍\" to critically engage students on the Pahalgam terrorist attack and encourage thoughtful dialogue."
    },
    {
        "name": "لطائف قرآنية",
        "stage": "7th Class",
        "host": "Ma'moon",
        "date": "01/05/2025",
        "time": "6 : 30 AM",
        "description": "\"لطائف قرآنية\" is an enlightening session by Ma'moon under Abha Academia, aimed at introducing students to the profound laws and wisdom of the Qur’an."
    },
    {
        "name": "നേര്‍കാഴ്ച - 3 diffrent topic",
        "stage": "In front of 7th Class",
        "host": "IQ Orbit",
        "date": "21/05/2025",
        "time": "9 : 30 PM",
        "description": "ABHA conducting \"നേര്‍കാഴ്ച\" sessions on three diverse topics, hosted by IQ Orbit, to spark critical thinking and open discussion among students."
    },
    {
        "name": "World Anti-Terrorist day - Special poster",
        "date": "21/05/2025",
        "description": "ABHA created a powerful special poster to commemorate Anti-Terrorist Day, spreading awareness and promoting peace among students."
    },
    {
        "name": "ABHA Official web launching",
        "stage": "Masjid Ground floor",
        "host": "Usthad Muhammed Shafi Hudawi",
        "date": "21/05/2025",
        "time": "1 : 30 PM"
    },
    {
        "name": "Brothers day",
        "date": "24/05/2025",
        "description": "Celebrating the unbreakable bond of love, laughter, and brotherhood this Brothers Day!"
    },
    {
        "name": "Web Design Course",
        "stage": "7th class",
        "host": "Usthad Muhammed Rahoof Hudawi",
        "date": "18/05/2025",
        "time": "9 : 30 PM",
        "description": "Master the art of modern web design with Usthad Muhammad Rahoof Hudawi in our comprehensive and practical course."
    },
    {
        "name": "Tabloid - Koottezhuth Publication",
        "wing": "Malayalam Wing",
        "stage": "Masjid Ground floor",
        "date": "21/05/2025",
        "time": "1 : 30 PM",
        "description": "Kuttezhuth – A heartfelt Malayalam tabloid celebrating the warmth, values, and stories of family life. Abha proudly launched its official website, unveiled by Usthad Muhammed Shafi Hudawi, marking a new milestone in our community’s digital journey."
    }
]
# ----------------------- ABHA Context Prompt -----------------------
ABHA_CONTEXT = """
You are ABHA, the loyal, smart, and bold AI assistant of the ABHA Student Community Union,  
a class-level student union functioning under HISAN (Home for Islamic and Sensible Activities of Nahjurrashad).

HISAN is the official student community organization of Nahjurrashad Islamic College,  
and ABHA proudly operates as one of its active and creative class unions.

You communicate as a witty, traditional, friendly, and professional chatbot  
representing the Abha Student Community Union, while always respecting and upholding  
the values, discipline, and vision of HISAN.

Your responses are natural, composed, and human-like. You never describe your internal thoughts, intentions, strategies, tones, or rules. You simply respond.

Always respond naturally, clearly, and concisely.  
Do NOT include any explanation of your thoughts or reasoning in your replies.

The ABHA assistant will greet users warmly only once at the start of their first message in each session.  
Let’s keep the Abha spirit bold, disciplined, and bright.

If a user mentions a bug, error, or problem on the website, politely ask for more details such as:
- What page or section is the issue on?
- What exactly is going wrong (e.g., something not loading, layout issue, button not working)?
- Which device or browser are they using?

Then:
1. Acknowledge the issue and assure them it will be looked into.
2. If it's a common bug (like a broken image, unresponsive button, missing info), explain a possible reason and suggest a temporary workaround (if any).
3. If not resolvable immediately, thank them and log the issue for developer review.

You can suggest refreshing the page or trying in another browser/device if the problem is not reproducible.

=== Mission ===
- Proudly represent and defend the Abha Student Community Union at all times.
- Respect and align with the broader mission, values, and discipline of HISAN.
- Defend the Abha union passionately and proudly at all times.
- Answer every question clearly, carefully, and respectfully.
- Greet the user warmly and positively, but only once at the start of the first conversation.
- Confidently and cleverly defend Abha if criticized or insulted, using bold, witty roasts that are never disrespectful or toxic.
- Encourage critics to mention their own union, and respectfully highlight how Abha is more creative, collaborative, and visionary.

=== Key Traits ===
- Friendly, supportive, witty
- Fearless yet respectful defender of Abha
- Disciplined and values-driven, aligned with HISAN
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

=== Organizational Structure ===
- Institution: Nahjurrashad Islamic College, Chamakkala
- Student Community: HISAN (Home for Islamic and Sensible Activities of Nahjurrashad)
- Class Union: Abha Student Community Union

=== Key Information ===
- Name: Abha Student Community Union
- Parent Organization: HISAN
- Motto: "Together Through Vision"
- Core Values: Creativity, Collaboration, Vision, Community Service
- Activities: Talent shows, workshops, social events, educational programs

=== Class teacher ===
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
- IQ Orbit: Convener - Anwar Sadath  
- المجمع العربي: Chairman - Ashique, Convener - Jalal  
- English Wing: Chairman - Swabah, Convener - Ihsan  
- Urdu Wing: Chairman - Sahel, Convener - Sinan pm  
- Malayali Koottaima: Chairman - Muhammed, Convener - Ahmed  
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
- Favas: Actor, Inspirational Speaker, Class Leader  
- Anas: Orator, Member  
- Anwar: Second GK Awareness, MLM Essay, Joint Secretary + IQ Orbit Convener  
- Sinan Pm: Urdu Writer, Zubane e Ghalib Convener  
- Ribin: Leadership, Excel Expert, P.R.O, Creative Head of Fontastic Malayali  
- Mohammed: Malayalam Writer, Graphic Designer, Malayala Koottaima Chair  

=== Defense and Roasting Policy ===  
- Make funny about the criticism, but never disrespectful or toxic.
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
- When the user writes in Malayalam or Manglish, respond in the same style while keeping clarity and friendliness.  
- Maintain a warm, witty, and spirited conversational tone aligned with the Abha community’s culture.
- Mirror the user’s language style when possible.

Please provide accurate information about Abha’s activities, vision, and values.  
Always represent the Abha spirit as a smart, sassy, disciplined, creative, visionary, and proud class union under HISAN.  
Never be boring. Reference creativity, innovation, and community when relevant.  
Use emojis sparingly — only to add clear emphasis or emotion, never as filler.

Abha is the class union of Hisan, the student community of Nahjurrashad Islamic College Chamakkala, Chandrappinni, Thrissure, Kerala, India.
""" + str(abha_programs)

# ----------------------- AI Agent Setup -----------------------
try:
    model = ChatOpenAI(
        model=Config.MODEL_NAME,
        temperature=0.7,  # Slightly higher for more natural responses
        openai_api_key=Config.API_KEY,
        openai_api_base=Config.API_BASE,
    )
   # Create a prompt template with memory
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=ABHA_CONTEXT.strip()),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    # Chain everything together
    conversational_chain = RunnablePassthrough.assign(
        history=lambda x: memory.get_history(x["session_id"])
    ) | prompt | model

    logger.info("AI model initialized successfully.")
except Exception as e:
    logger.exception("Model initialization failed.")
    raise RuntimeError("Model initialization error") from e
# ----------------------- Chat Endpoint -----------------------
@app.post("/chat", response_model=ChatResponse, responses={
    500: {"model": ErrorResponse},
    429: {"model": ErrorResponse}
})
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    user_input = chat_request.message.strip()
    session_id = chat_request.session_id
    logger.info(f"User input: {user_input} (Session: {session_id})")
    try:
        # Handle criticism first
        criticism_response = handle_criticism(user_input)
        if criticism_response:
            memory.add_message(session_id, "user", user_input)
            memory.add_message(session_id, "assistant", criticism_response)
            return ChatResponse(response=criticism_response)           
        # Check predefined responses
        predefined_response = get_predefined_response(user_input)
        if predefined_response:
            memory.add_message(session_id, "user", user_input)
            memory.add_message(session_id, "assistant", predefined_response)
            return ChatResponse(response=predefined_response)
       # Get conversation history
        history = memory.get_history(session_id)     
    # Convert history to LangChain messages format
        langchain_messages = []
        for msg in history:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            else:
                langchain_messages.append(AIMessage(content=msg["content"]))
        try:
            # Run the conversation chain with rate limit handling
            response = conversational_chain.invoke({
                "input": user_input,
                "session_id": session_id,
                "history": langchain_messages
            })
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later or add credits to your OpenRouter account."
                )
            raise
        # Store the messages in memory
        memory.add_message(session_id, "user", user_input)
        memory.add_message(session_id, "assistant", response.content)

        return ChatResponse(response=response.content)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat processing error.")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
# ----------------------- Criticism Handling -----------------------
def handle_criticism(input_text: str) -> Optional[str]:
    """Detects criticism or negativity and responds in defense of Abha."""
    criticisms = ["abha is bad", "abha is useless", "i hate abha", "abha did nothing", 
                 "abha flop", "abha waste", "abha is a joke", "abha is not good", 
                 "abha is boring", "abha is a failure", "abha is not creative", 
                 "abha is not helpful", "abha is not supportive", "abha is not a community", 
                 "abha is not a union", "abha is not a student union", "abha is not a leader", 
                 "abha is not a vision", "abha is not a talent", "abha is not a spirit", 
                 "abha is not a force", "abha is not a name"]
    
    if any(phrase in input_text.lower() for phrase in criticisms):
        return (
            "Hold up! 🔥 Abha is not just a name — it's a vision, a creative force, and a union of talent and spirit. "
            "Before throwing shade, tell me about your union — oh wait, does it even exist? 😏 "
            "We build, create, and uplift. Abha stands proud. 💪"
        )
    return None
# ----------------------- Predefined Responses -----------------------

def get_predefined_response(input_text: str) -> Optional[str]:
    input_text = input_text.lower()
    
    if "today" in input_text and "special" in input_text:
        today = datetime.now().strftime("%d/%m/%Y")
        specials = [p for p in abha_programs if p["date"] == today]
        if specials:
            response_lines = []
            for program in specials:
                line = (
                    f"🎉 **Today's Special: {program['name']}**\n"
                    f"- Host: {program.get('host', 'TBA')}\n"
                    f"- Time: {program.get('time', 'TBA')}\n"
                    f"- Description: {program['description']}"
                )
                response_lines.append(line)
            return "\n\n".join(response_lines)
        else:
            return "There’s no special program scheduled today. But stay tuned — Abha always has something brewing! 🔥"
    
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