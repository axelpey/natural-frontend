# fastapi-natural-frontend

Make your fastAPI generate a frontend to interact with it in one line

### Running the Application

1. First, install the required packages:
   `pip install -r requirements.txt`

2. Run the application:
   `uvicorn app.main:app --reload`

### (With Docker)

1. Make sure you have [Docker](https://docs.docker.com/engine/install/) installed

2. Run `docker build -t my_cool_image_name`

3. Run `docker run -d --name my_cool_container_name -p 80:80 my_cool_image_name`

### Notes

- This application is very basic and uses an in-memory list to store book data. For a real application, you'd want to use a database.
- The `Book` model in `models.py` uses Pydantic for data validation.
- The `main.py` file defines three API routes: to list all books (`GET /books`), add a new book (`POST /books`), and get a specific book by ID (`GET /books/{book_id}`).

With this basic structure, you can now integrate the natural language processing middleware or wrapper you plan to develop. This app serves as a straightforward starting point for your prototype.
