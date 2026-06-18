from fastapi import FastAPI
from fastapi import Body
from fastapi import Request
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy import Text

from typing import List

from app.models import ChatRequest
from app.models import ChatResponse
from app.models import HealthResponse
from app.models import BroadcastRequest

from app.database import get_db
from app.database import ChatHistory, Customer, User 
import json
import time


from app.services.mistral_service import generate_ai_response
from app.services.mistral_service import (
    generate_lead_summary
)
from app.services.whatsapp_service import (
    send_whatsapp_message
)

from pydantic import BaseModel

from app.auth import (
    create_access_token,
    verify_password,
    get_current_user,
    admin_required,
    manager_required,
    viewer_required
)

app = FastAPI()

# =====================================================
# LOGIN REQUEST MODEL
# =====================================================

class LoginRequest(BaseModel):
    username: str
    password: str
# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="WhatsApp AI Customer Support Agent",
    description="AI Customer Support Executive using Mistral AI",
    version="2.0.0"
)

# =========================================================
# HEALTH CHECK ROUTE
# =========================================================

@app.get("/", response_model=HealthResponse)
def home():

    return HealthResponse(
        status="success",
        message="WhatsApp AI Agent Running Successfully"
    )

# =====================================================
# ADMIN LOGIN
# =====================================================

# @app.post("/login")
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):

#     user = (
#         db.query(User)
#         .filter(
#             User.username == form_data.username
#         )
#         .first()
#     )

#     if not user:

#         raise HTTPException(
#             status_code=401,
#             detail="User not found"
#         )

#     if not verify_password(
#         form_data.password,
#         user.password
#     ):

#         raise HTTPException(
#             status_code=401,
#             detail="Invalid password"
#         )

#     access_token = create_access_token(
#         {
#             "sub": user.username,
#             "role": user.role
#         }
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user.role
#     }


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):


    user = (
        db.query(User)
        .filter(
            User.username == form_data.username
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@app.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    role: str = Depends(manager_required)

):

    total_customers = (
        db.query(Customer)
        .count()
    )

    total_messages = (
        db.query(ChatHistory)
        .count()
    )

    return {
        "total_customers": total_customers,
        "total_messages": total_messages
    }

@app.get("/customers")
def get_customers(
    db: Session = Depends(get_db),
    role: str = Depends(viewer_required)
):
    return db.query(Customer).all()


@app.get("/leads")
def get_leads(
    db: Session = Depends(get_db),
    role: str = Depends(viewer_required)
):
    leads = (
        db.query(Customer)
        .order_by(Customer.created_at.desc())
        .all()
    )

    return leads

@app.get("/lead/{phone}")
def get_lead(
    phone: str,
    db: Session = Depends(get_db),
    role: str = Depends(viewer_required)
):

    lead = (
        db.query(Customer)
        .filter(Customer.phone == phone)
        .first()
    )

    if not lead:
        return {
            "message": "Lead not found"
        }

    return lead

@app.get("/lead-summary/{phone}")
def lead_summary(
    phone: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(Customer.phone == phone)
        .first()
    )

    if not customer:
        return {
            "message": "Lead not found"
        }

    if customer.summary:

        summary = customer.summary

    else:

        summary = generate_lead_summary(
            customer
        )

        customer.summary = summary

        db.commit()

    return {
        "name": customer.name,
        "phone": customer.phone,
        "summary": summary
    }


@app.get("/search-leads")
def search_leads(
    name: str = None,
    phone: str = None,
    city: str = None,
    service: str = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    query = db.query(Customer)

    if name:
        query = query.filter(
            Customer.name.ilike(f"%{name}%")
        )

    if phone:
        query = query.filter(
            Customer.phone.ilike(f"%{phone}%")
        )

    if city:
        query = query.filter(
            Customer.city.ilike(f"%{city}%")
        )

    if service:
        query = query.filter(
            Customer.service.ilike(f"%{service}%")
        )

    return [
        {
            "name": lead.name,
            "phone": lead.phone,
            "city": lead.city,
            "service": lead.service,
            "budget": lead.budget
        }
        for lead in query.all()
    ]

@app.get("/chat-history/{phone}")
def get_chat_history(
    phone: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == phone)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    return chats

@app.get("/all-chats")
def all_chats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ChatHistory).all()


@app.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    role: str = Depends(manager_required)
):

    total_leads = db.query(Customer).count()

    male_leads = (
        db.query(Customer)
        .filter(Customer.gender == "male")
        .count()
    )

    female_leads = (
        db.query(Customer)
        .filter(Customer.gender == "female")
        .count()
    )

    ai_solutions = (
        db.query(Customer)
        .filter(Customer.service == "AI Solutions")
        .count()
    )

    data_analytics = (
        db.query(Customer)
        .filter(Customer.service == "Data Analytics")
        .count()
    )

    software_development = (
        db.query(Customer)
        .filter(Customer.service == "Software Development")
        .count()
    )

    whatsapp_automation = (
        db.query(Customer)
        .filter(Customer.service == "WhatsApp Automation")
        .count()
    )

    return {
        "total_leads": total_leads,
        "male_leads": male_leads,
        "female_leads": female_leads,
        "ai_solutions": ai_solutions,
        "data_analytics": data_analytics,
        "software_development": software_development,
        "whatsapp_automation": whatsapp_automation
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    try:

# =================================================
# CLEAN USER MESSAGE
# =================================================

        user_message = request.message.strip()

        # =================================================
        # EMPTY MESSAGE VALIDATION
        # =================================================

        if not user_message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        # =================================================
        # FETCH CONVERSATION HISTORY
        # =================================================

        conversation_history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.session_id == request.session_id
            )
            .order_by(ChatHistory.created_at.asc())
            .all()
        )

        # =================================================
        # GENERATE AI RESPONSE WITH MEMORY
        # =================================================

        ai_reply = generate_ai_response(
            user_message=user_message,
            conversation_history=conversation_history,
            user_name="User"
        )

        # =================================================
        # SAVE CHAT HISTORY TO DATABASE
        # =================================================

        chat_data = ChatHistory(
            session_id=request.session_id,
            user_message=user_message,
            ai_reply=ai_reply
        )

        db.add(chat_data)

        db.commit()

        db.refresh(chat_data)

        # =================================================
        # RETURN RESPONSE
        # =================================================

        return ChatResponse(
            session_id=request.session_id,
            user_message=user_message,
            ai_reply=ai_reply
        )

    except HTTPException:
        raise

    except Exception as e:

        print("MAIN API ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@app.post("/broadcast")
def broadcast_message(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    role: str = Depends(admin_required)
):

    customers = db.query(Customer).all()

    sent_count = 0
    message = request.message

    for customer in customers:

        try:

            send_whatsapp_message(
                customer.phone,
                message
            )

            sent_count += 1

        except Exception as e:

            print(
                f"Broadcast Failed: {customer.phone}"
            )

    return {
        "status": "success",
        "message_sent_to": sent_count
    }
# =========================================================
# WHATSAPP WEBHOOK VERIFICATION
# =========================================================

from fastapi import Query, HTTPException

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db)
):

    try:

        # =====================================================
        # RECEIVE WEBHOOK DATA
        # =====================================================

        body = await request.json()

        print("\n" + "=" * 50)
        print("WHATSAPP MESSAGE RECEIVED")
        print(json.dumps(body, indent=2))
        print("=" * 50 + "\n")

        # =====================================================
        # CHECK IF MESSAGE EXISTS
        # =====================================================

        value = (
            body["entry"][0]
            ["changes"][0]
            ["value"]
        )

        if "messages" not in value:
            return {
                "status": "ignored"
            }

        # =====================================================
        # EXTRACT MESSAGE DATA
        # =====================================================

        message = value["messages"][0]
        sender = message["from"]


# =====================================================
# USER MESSAGE
# =====================================================

        user_message = message["text"]["body"].strip()

        print(f"Sender: {sender}")
        print(f"Message: {user_message}")        

        # ==========================================
        # GET WHATSAPP PROFILE NAME
        # ==========================================

        # contact_name = "User"
        # if "contacts" in value:
        #     contact_name = (
        #         value["contacts"][0]
        #         ["profile"]
        #         ["name"]
        #     )

        # print(f"Contact Name: {contact_name}")


        # =====================================================
        # FIND CUSTOMER
        # =====================================================

        customer = (
            db.query(Customer)
            .filter(Customer.phone == sender)
            .first()
        )

        if (
            "connect" in user_message.lower() or
            "call" in user_message.lower() or
            "team" in user_message.lower() or
            "human" in user_message.lower() or
            "support" in user_message.lower() or
            "representative" in user_message.lower() or
            "agent" in user_message.lower()

        ):
            
            customer.stage = "completed"
            db.commit()

            send_whatsapp_message(
                sender,

                """"
Thank you. 😊

Our team will contact you shortly.

📧 Email:
omendra8285@gmail.com

📞 Mobile:
8285808465
"""
            )

            return {
                "status": "success"
            }

        # =====================================================
        # NEW CUSTOMER
        # =====================================================

        if not customer:

            customer = Customer(
                phone=sender,
                stage="name"
            )

            db.add(customer)
            db.commit()

            send_whatsapp_message(
                sender,
                "👋 Welcome to Omendra AI Support.\n\nPlease tell me your name."
            )

            return {"status": "success"}

        # =====================================================
        # NAME
        # =====================================================

        if customer.stage == "name":

            customer.name = user_message
            customer.stage = "gender"

            db.commit()

            send_whatsapp_message(
                sender,
                f"Nice to meet you {customer.name}! 😊\n\nWhat is your gender?\n\n1. Male\n2. Female\n3. Other"
            )

            return {"status": "success"}

        # =====================================================
        # GENDER
        # =====================================================

        if customer.stage == "gender":

            customer.gender = user_message
            customer.stage = "age"

            db.commit()

            send_whatsapp_message(
                sender,
                "Thank you.\n\nPlease enter your age."
            )

            return {"status": "success"}

        # =====================================================
        # AGE
        # =====================================================

        if customer.stage == "age":

            customer.age = user_message
            customer.stage = "city"

            db.commit()

            send_whatsapp_message(
                sender,
                "Great.\n\nWhich city are you from?"
            )

            return {"status": "success"}

        # =====================================================
        # CITY
        # =====================================================

        if customer.stage == "city":

            customer.city = user_message
            customer.stage = "service"

            db.commit()

            send_whatsapp_message(
                sender,
                """Please select a service:

        1. AI Solutions
        2. Data Analytics
        3. Software Development
        4. WhatsApp Automation"""
            )

            return {"status": "success"}

        # =====================================================
        # SERVICE
        # =====================================================

        if customer.stage == "service":

            customer.service = user_message
            customer.stage = "requirement"

            db.commit()

            send_whatsapp_message(
                sender,
                "Please describe your requirement."
            )

            return {"status": "success"}

        # =====================================================
        # REQUIREMENT
        # =====================================================

        if customer.stage == "requirement":

            customer.requirement = user_message
            customer.stage = "budget"

            db.commit()

            send_whatsapp_message(
                sender,
                """Please select your budget:

        1. Below ₹10,000
        2. ₹10,000 - ₹50,000
        3. Above ₹50,000"""
            )

            return {"status": "success"}

        # =====================================================
        # BUDGET
        # =====================================================

        if customer.stage == "budget":

            customer.budget = user_message
            customer.stage = "completed"

            db.commit()

            send_whatsapp_message(
                sender,
                f"""Thank you {customer.name}! 🎉

        Your details have been recorded.

        Our team will contact you shortly.

        📧 Email:
        omendra8285@gmail.com

        📞 Mobile:
        8285808465

        You can continue asking questions about:
        1. AI Solutions
        2. Data Analytics
        3. Software Development
        4. WhatsApp AI Automation"""
            )

            return {"status": "success"}

        # =====================================================
        # COMPLETED
        # =====================================================

        contact_name = customer.name if customer.name else "User"

        # =====================================================
        # FETCH CONVERSATION HISTORY
        # SESSION ID = PHONE NUMBER
        # =====================================================

        conversation_history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.session_id == sender
            )
            .order_by(
                ChatHistory.created_at.asc()
            )
            .all()
        )

        # =====================================================
        # GENERATE AI RESPONSE
        # =====================================================

        print("STEP 1: CALLING MISTRAL")
        time.sleep(1)  # Simulate typing delay

        ai_reply = generate_ai_response(
            user_message=user_message,
            conversation_history=conversation_history,
            user_name=contact_name
        )

        print("STEP 2: AI REPLY GENERATED")
        print(f"AI Reply: {ai_reply}")

        # =====================================================
        # SAVE CHAT TO DATABASE
        # =====================================================

        chat_data = ChatHistory(
            session_id=sender,
            user_name=contact_name,
            user_message=user_message,
            ai_reply=ai_reply
        )

        db.add(chat_data)
        db.commit()
        db.refresh(chat_data)

        # =====================================================
        # SEND REPLY TO WHATSAPP
        # =====================================================

        print("STEP 3: SENDING WHATSAPP MESSAGE")
        send_whatsapp_message(sender, ai_reply)
        print("STEP 4: WHATSAPP MESSAGE SENT")

        return {
            "status": "success"
        }

    except Exception as e:
        print("WEBHOOK ERROR:", repr(e))

        import traceback
        traceback.print_exc()

        return {
            "status": "error",
            "message": str(e)
        }



# =========================================================
# RUN SERVER
# =========================================================

# Run command:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Note: --host 0.0.0.0 allows external access to the server
#       --port 8000 specifies the port to run the server on
# =========================================================

# ngrok command for exposing local server:
# ngrok http 8000
# cd C:\Users\omend\Downloads\ngrok-v3-stable-windows-amd64
# .\ngrok.exe http 8000   
# This will give you a public URL that tunnels to your local server.