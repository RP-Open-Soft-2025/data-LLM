
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ChatBot.chatbot import router as chatbot_router
from Pipeline1.report import router as report_router

app = FastAPI(
    title="Employee Analysis API",
    description="API for analyzing employee behavior and mood data and for chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router, prefix="/chatbot")
app.include_router(report_router, prefix="/report")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080)