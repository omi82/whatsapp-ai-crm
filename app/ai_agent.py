from mistralai import Mistral
from dotenv import load_dotenv
from app.prompts import SYSTEM_PROMPT
import os

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# GET API KEY
# =========================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in .env file")

# =========================================================
# INITIALIZE MISTRAL CLIENT
# =========================================================

client = Mistral(api_key=MISTRAL_API_KEY)

# =========================================================
# GENERATE AI RESPONSE FUNCTION
# =========================================================

def generate_ai_response(
    user_message: str,
    conversation_history: list
) -> str:

    try:

        # =================================================
        # CLEAN USER INPUT
        # =================================================

        user_message = user_message.strip()

        # =================================================
        # EMPTY MESSAGE VALIDATION
        # =================================================

        if not user_message:
            return "Please enter a valid message."

        # =================================================
        # START MESSAGE LIST
        # =================================================
        #
        # This list is sent to Mistral AI.
        #
        # Structure:
        # System Prompt
        # Previous Conversations
        # Current User Message
        #
        # =================================================

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        # =================================================
        # ADD CONVERSATION MEMORY
        # =================================================
        #
        # NEW CHANGE 🚀
        #
        # WHY?
        #
        # This gives memory/context to AI.
        #
        # Previous chats are injected
        # before current message.
        #
        # This creates conversational AI.
        #
        # =================================================

        for chat in conversation_history:

            # Previous user message
            messages.append({
                "role": "user",
                "content": chat.user_message
            })

            # Previous AI reply
            messages.append({
                "role": "assistant",
                "content": chat.ai_reply
            })

        # =================================================
        # ADD CURRENT USER MESSAGE
        # =================================================

        messages.append({
            "role": "user",
            "content": user_message
        })

        # =================================================
        # MISTRAL API CALL
        # =================================================

        response = client.chat.complete(
            model="mistral-small-latest",

            messages=messages,

            temperature=0.5,
            max_tokens=150
        )

        # =================================================
        # EXTRACT AI RESPONSE
        # =================================================

        ai_reply = response.choices[0].message.content

        # =================================================
        # FALLBACK RESPONSE
        # =================================================

        if not ai_reply:
            ai_reply = "Our support team will contact you shortly."

        return ai_reply

    except Exception as e:

        print("AI AGENT ERROR:", str(e))

        return "Our support team will contact you shortly."