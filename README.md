<p align=center>
<img height="90px" src="https://github.com/axelpey/natural-frontend/assets/1381992/a11640b3-77af-4780-b40a-e3695a265091" alt="Natural Frontend Logo" />

<p align=center>
<b>From backend to frontend with one line</b> <br /> Don't waste hours generating a frontend for your users.

<p align=center>
<img height="240px" src="https://github.com/axelpey/natural-frontend/assets/1381992/87ccd4f5-f3a1-404e-940e-a92a7a1f47cc" alt="NF Usage" />

<p align=center>
<img width="600px" alt="NF Screenshot" src="https://github.com/axelpey/natural-frontend/assets/1381992/355d8553-50c1-48ac-be90-18b058eebc93">

## Features

TODO

## Development

We're happy to get contributors working with us! Follow the instructions below to quickly setup yo

### Running the Application
0. *(Optional)* Use virtualenv to quickly setup your environment:
   `virtualenv venv && source venv/bin/activate`

1. Install the required packages:
   `pip install -r requirements.txt`

2. Run the example application:
   `uvicorn app.main:app --reload`

### (With Docker)

1. Make sure you have [Docker](https://docs.docker.com/engine/install/) installed

2. Run `docker compose up --build`

### Notes

- The template application is very basic and uses an in-memory list to store book data. For a real application, you'd want to use a database.
- The `Book` model in `models.py` uses Pydantic for data validation.
- The `main.py` file defines three API routes: to list all books (`GET /books`), add a new book (`POST /books`), and get a specific book by ID (`GET /books/{book_id}`).

With this basic structure, you can now integrate the natural language processing middleware or wrapper you plan to develop. This app serves as a straightforward starting point for your prototype.
