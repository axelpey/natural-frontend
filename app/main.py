from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query

from src.fastapi_natural_frontend import NaturalFrontend, NaturalFrontendOptions
from app.models import Book
from app.db import books_db

app = FastAPI()

app = NaturalFrontend(app)


@app.get("/books")
async def get_books():
    return books_db


@app.post("/books")
async def add_book(book: Book):
    books_db.append(book.dict())
    return {"message": "Book added successfully"}


@app.get("/books/search", response_model=List[Book])
async def search_books(
    title: Optional[str] = Query(None, min_length=3),
    author: Optional[str] = Query(None, min_length=3),
    genre: Optional[str] = Query(None),
):
    query_result = books_db

    if title:
        query_result = [
            book for book in query_result if title.lower() in book["title"].lower()
        ]

    if author:
        query_result = [
            book for book in query_result if author.lower() in book["author"].lower()
        ]

    if genre:
        query_result = [
            book for book in query_result if genre.lower() == book["genre"].lower()
        ]

    return query_result


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: Book):
    index = next(
        (index for (index, d) in enumerate(books_db) if d["id"] == book_id), None
    )

    if index is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book_dict = book.dict()
    book_dict["id"] = book_id
    books_db[index] = book_dict
    return book_dict


@app.delete("/books/{book_id}", response_model=Book)
async def delete_book(book_id: int):
    index = next(
        (index for (index, d) in enumerate(books_db) if d["id"] == book_id), None
    )

    if index is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return books_db.pop(index)
