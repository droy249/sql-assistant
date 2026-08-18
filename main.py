
import logging
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import init_database
from agent import run_agent

# Set up request logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a FastAPI application instance with metadata
app = FastAPI(
    title="AI SQL Assistant API",
    description="An AI-powered REST API that answers natural language questions about a sales database using Claude's tool-calling capabilities.",
    version="1.0.0",
)

# Enable CORS on the actual running app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Initialize the database when the app starts
init_database()

# Simple in-memory store for conversation histories
conversations: dict = {}


class AskRequest(BaseModel):
    # The natural language question from the user
    question: str
    conversation_id: str | None = None


class TokenUsage(BaseModel):
    input: int
    output: int


class AskResponse(BaseModel):
    question: str
    query: str | None
    results: list | None
    answer: str
    tokens_used: TokenUsage
    response_time_ms: int
    conversation_id: str | None = None


@app.get("/health")
def health_check():
    """Simple endpoint to verify the API is running."""
    return {"status": "healthy"}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    logger.info(f"Question received: {request.question}")
    start_time = time.time()

    # Load conversation history if continuing a conversation
    messages = None
    if request.conversation_id:
        messages = conversations.get(request.conversation_id, [])
        # Limit to last 10 message pairs (20 messages) to stay within context limits
        if len(messages) > 20:
            messages = messages[-20:]

    # Call the agent and handle API failures
    try:
        result = run_agent(request.question, messages=messages)
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Return 400 if the agent blocked the SQL query
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["answer"])
    
    # Store updated conversation history for follow-up questions
    if request.conversation_id and messages is not None:
        conversations[request.conversation_id] = messages

    logger.info(
        f"SQL: {result['query']} | Time: {result['response_time_ms']}ms | Tokens: {result['tokens_used']}"
    )

    return AskResponse(
        question=result["question"],
        query=result["query"],
        results=result["results"],
        answer=result["answer"],
        tokens_used=TokenUsage(**result["tokens_used"]),
        response_time_ms=result["response_time_ms"],
        conversation_id=request.conversation_id,
    )