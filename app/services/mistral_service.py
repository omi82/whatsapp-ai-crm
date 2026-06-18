from mistralai import Mistral
from dotenv import load_dotenv
import os
from app.services.rag_service import (
    search_company_knowledge
)
# =========================================================

# LOAD ENV VARIABLES

# =========================================================

load_dotenv()

# =========================================================

# GET API KEY

# =========================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY not found in .env")

# =========================================================

# INITIALIZE MISTRAL CLIENT

# =========================================================

client = Mistral(
api_key=MISTRAL_API_KEY
)

# =========================================================

# SYSTEM PROMPT

# =========================================================

SYSTEM_PROMPT = """
You are a professional customer support executive.

Company Name:
Omendra AI Support

Responsibilities:

* Answer customer questions politely
* Keep responses short and professional
* Help customers understand services
* Maintain conversation context
* If unsure, say:
  'Our support team will contact you shortly.'

Services:

1. AI Solutions
2. Data Analytics
3. Software Development
4. WhatsApp AI Automation

Rules:

* Never provide fake information
* Never create fake pricing
* Keep responses under 100 words
  """

# =========================================================

# GENERATE AI RESPONSE WITH MEMORY

# =========================================================

def generate_ai_response(
    user_message: str,
    conversation_history=None,
    user_name: str = "User"
) -> str:

    try:

        knowledge = search_company_knowledge(
            user_message
        )

        messages = [
            {
                "role": "system",
                "content": f"""
        {SYSTEM_PROMPT}

        COMPANY KNOWLEDGE:

        {knowledge}

        Instructions:

        - Answer only using the company knowledge provided.
        - If information is not available in company knowledge, say:
          "Please contact our support team for this information."
        - Do not create timings, pricing, policies, or commitments.
        - Do not invent facts.
        - Keep responses short and professional.
        """
            }
        ]

        # =================================================
        # ADD PREVIOUS CONVERSATION MEMORY
        # =================================================

        if conversation_history:

            for chat in conversation_history:

                messages.append(
                    {
                        "role": "user",
                        "content": chat.user_message
                    }
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": chat.ai_reply
                    }
                )

        # =================================================
        # CURRENT USER MESSAGE
        # =================================================

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        # =================================================
        # MISTRAL API CALL
        # =================================================

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )

        ai_reply = response.choices[0].message.content

        # =================================================
        # FALLBACK RESPONSE
        # =================================================

        if not ai_reply:

            return (
                "Our support team will contact you shortly."
            )

        return ai_reply

    except Exception as e:

        print(
            "MISTRAL ERROR:",
            str(e)
        )

        return (
            "Our support team will contact you shortly."
        )


def generate_lead_summary(customer):

    prompt = f"""
Create a professional lead summary.

Name: {customer.name}
Gender: {customer.gender}
Age: {customer.age}
City: {customer.city}

Service: {customer.service}
Requirement: {customer.requirement}
Budget: {customer.budget}

Write:
1. Short Lead Summary
2. Customer Need
3. Recommended Follow Up

Keep under 100 words.
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
