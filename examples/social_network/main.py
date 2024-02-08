from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from natural_frontend.natural_frontend import NaturalFrontend, NaturalFrontendOptions

app = FastAPI()

# Open the creds.json
with open("creds.json") as f:
    creds = json.load(f)

app = NaturalFrontend(
    app,
    openai_api_key=creds["key"],
    options=NaturalFrontendOptions(frontend_endpoint=""),
)


class User(BaseModel):
    id: int
    email: str
    name: Optional[str] = None


class Post(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime = datetime.now()


# Initial data
users = [
    User(id=1, email="user1@example.com", name="User One"),
    User(id=2, email="user2@example.com", name="User Two"),
]
posts = [
    Post(id=1, title="Post 1", content="Content of post 1", owner_id=1),
    Post(id=2, title="Post 2", content="Content of post 2", owner_id=1),
    Post(id=3, title="Post 3", content="Content of post 3", owner_id=2),
]


@app.post("/users/", response_model=User)
def create_user(user: User):
    users.append(user)
    return user


@app.get("/users/", response_model=List[User])
def get_users():
    return users


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/posts/", response_model=Post)
def create_post(post: Post):
    posts.append(post)
    return post


@app.get("/posts/", response_model=List[Post])
def get_posts():
    return posts


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    for post in posts:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")
