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
    User(id=1, email="axel@mail.com", name="Axel Peytavin"),
    User(id=2, email="pierrot@great-ai-startup.com", name="Pierre"),
    User(id=3, email="michelle@aol.com", name="Michelle"),
]
posts = [
    Post(id=1, title="I love my dog", content="I love my dog a lot", owner_id=1),
    Post(id=2, title="I love my cat", content="He's so cute", owner_id=1),
    Post(
        id=3, title="Who left the door open?", content="I'm freezing here", owner_id=2
    ),
    Post(id=4, title="I'm so happy", content="I just got a new job", owner_id=3),
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
