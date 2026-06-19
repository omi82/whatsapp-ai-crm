# WhatsApp AI CRM

Enterprise-grade AI-powered CRM platform built with:

- FastAPI
- PostgreSQL
- Streamlit
- Mistral AI
- JWT Authentication
- WhatsApp Cloud API
- RAG (Retrieval Augmented Generation)

## Features

- WhatsApp Customer Support Agent
- Lead Qualification
- Customer CRM
- Broadcast Messaging
- AI Chat History
- Analytics Dashboard
- Role-Based Access Control

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Streamlit
- SQLAlchemy
- JWT
- Mistral AI

## Project Structure

app/
admin/
requirements.txt

## Environment Variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_api_key
WHATSAPP_TOKEN=your_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_verify_token
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key

## Run Backend

```bash
uvicorn app.main:app --reload