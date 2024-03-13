<p align=center>
<img height="90px" src="https://github.com/axelpey/natural-frontend/assets/1381992/a11640b3-77af-4780-b40a-e3695a265091" alt="Natural Frontend Logo" />

<p align=center>
<b>From backend to frontend with one line</b> <br /> Don't waste hours generating a frontend for your users.

<p align=center>
<img height="200px" src="https://github.com/axelpey/natural-frontend/assets/1381992/ab776a2b-2f64-4022-bfd2-7cdd3d9084ad" alt="NF Usage" />

https://github.com/axelpey/natural-frontend/assets/1381992/dbef93fa-6313-4122-902b-9109961abeec


## Features

- Works with 2 major backend frameworks: (https://flask.palletsprojects.com/en/2.3.x/)[Flask] and (https://fastapi.tiangolo.com/)[FastAPI]
- Natural Frontend understands your codebase and the potential user personas for your product.
- On the `/frontend` endpoint, select a user persona and NF will generate a tailored frontend.

*Coming soon*:
- Save your generated frontends to modify them later.
- Use local models instead of OpenAI.

## Usage

### ⬇️ Installation

With pip: `pip install natural-frontend`

### ➕ Add to your code

#### With FastAPI

Just add one-line to your api project:

```python
from fastapi import FastAPI
from natural_frontend import NaturalFrontend

openai_key = "sk-..."

app = FastAPI()
app = NaturalFrontend(app, openai_key)

@app.get("/books")
async def get_books():
    return books_db


@app.post("/books")
async def add_book(book: Book):
    books_db.append(book.dict())
    return {"message": "Book added successfully"}

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
```

#### With Flask

It's the same!

```python
from flask import Flask
from natural_frontend import NaturalFrontend

openai_key = "sk-..."

app = Flask(__name__)
app = NaturalFrontend(app, openai_key)
```

### ⚙️ Options

You can provide options to customize your Natural Frontend:

```python
nf_options = NaturalFrontendOptions(
   colors={"primary": "lightblue", "secondary": "purple"},
   personas=[{"Bookworm": "Loves to look for new books"}],
   cache_expiry_time=600,
   frontend_endpoint="frontend",
)

app = NaturalFrontend(app, openai_key, nf_options)
```

Documentation of options:
- `colors`: Customize the color themes of the frontend. Use two keys: "primary" and "secondary".
- `personas`: Add custom personas for your frontend. NF will guess more until there's a total of 5 personas.
- `cache_expiry_time`: Set the time in seconds before the generation cache expires.
- `frontend_endpoint`: Change the endpoint of the frontend.

## Development

We're happy to get contributors working with us! Follow the instructions below to quickly setup your local environment.

### Running the Application
0. *(Optional)* Use virtualenv to quickly setup your environment:
   `virtualenv venv && source venv/bin/activate`

1. Install the required packages:
   `pip install -r requirements.txt`

2. Run one of the example applications:
   `uvicorn example.APP.main:app --reload` where APP is one in the `examples` directory.

### (With Docker)

1. Make sure you have [Docker](https://docs.docker.com/engine/install/) installed

2. Run `docker compose up --build`
