import uvicorn
from fastapi import FastAPI, HTTPException
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

# Global variable for testing CRUD operations
items = []  # This list will hold our items
next_id = 1  # Simple auto-increment id for each new item

@app.get("/items")
def get_items():
    """Retrieve all items."""
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Retrieve a single item by ID."""
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items")
def create_item(item: dict):
    """Create a new item. Expects a JSON body, e.g. {'name': 'Item1', 'description': 'A test item'}."""
    global next_id
    new_item = {"id": next_id, **item}
    next_id += 1
    items.append(new_item)
    return new_item

@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: dict):
    """Update an existing item by ID."""
    for index, item in enumerate(items):
        if item["id"] == item_id:
            updated = {"id": item_id, **updated_item}
            items[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Delete an item by ID."""
    global items
    for item in items:
        if item["id"] == item_id:
            items = [it for it in items if it["id"] != item_id]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080)
    
