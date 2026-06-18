from pydantic import BaseModel, Field
from datetime import datetime

# =========================================================
# CHAT REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    # =====================================================
    # NEW CHANGE
    # SESSION ID
    # =====================================================
    #
    # WHY ADDED?
    #
    # Helps identify unique users/conversations.
    #
    # Example:
    # user_101
    # whatsapp_9876543210
    #
    # Same session_id = same conversation memory
    #
    # =====================================================

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique customer session ID"
    )

    # =====================================================
    # CUSTOMER MESSAGE
    # =====================================================

    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Customer message"
    )

# =========================================================
# CHAT RESPONSE MODEL
# =========================================================

class ChatResponse(BaseModel):

    # =====================================================
    # NEW CHANGE
    # RETURN SESSION ID
    # =====================================================
    #
    # WHY ADDED?
    #
    # Helps frontend/client know
    # which conversation belongs to which user.
    #
    # =====================================================

    session_id: str

    user_message: str
    ai_reply: str

# =========================================================
# HEALTH CHECK RESPONSE MODEL
# =========================================================

class HealthResponse(BaseModel):

    status: str
    message: str

# =========================================================
# CHAT HISTORY RESPONSE MODEL
# =========================================================

class ChatHistoryResponse(BaseModel):

    id: int

    # =====================================================
    # NEW CHANGE
    # SESSION ID IN CHAT HISTORY
    # =====================================================

    session_id: str
    user_name: str | None = None
    user_message: str
    ai_reply: str
    created_at: datetime

    # =====================================================
    # Pydantic v2 ORM Support
    # =====================================================

    model_config = {
        "from_attributes": True
    }


# =========================================================
# BROADCAST REQUEST MODEL
# =========================================================

class BroadcastRequest(BaseModel):
    message: str

