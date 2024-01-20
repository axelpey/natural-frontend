from fastapi import FastAPI, HTTPException

from src.fastapi_natural_frontend import add_natural_frontend
from app.models import Book

app = FastAPI()

app = add_natural_frontend(app)

# In-memory 'database' for prototype
books_db = [
    {"id": 1, "title": "1984", "author": "George Orwell"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
]


@app.get("/books")
async def get_books():
    return books_db


@app.post("/books")
async def add_book(book: Book):
    books_db.append(book.dict())
    return {"message": "Book added successfully"}


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")
