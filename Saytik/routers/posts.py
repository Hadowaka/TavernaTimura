"""
============================================================
  routers/posts.py  —  All Forum Post Endpoints
============================================================

WHAT THIS FILE DOES:
  Defines every HTTP route that deals with forum POSTS:
    GET    /posts            → list all posts
    GET    /posts/{id}       → get one post by ID
    POST   /posts            → create a new post
    PUT    /posts/{id}       → edit an existing post
    DELETE /posts/{id}       → delete a post

KEY CONCEPTS EXPLAINED HERE:
  • APIRouter      — a mini-app that groups related routes
  • Pydantic models — define the shape (schema) of request data
  • Path parameters — /posts/{post_id}
  • HTTP status codes — 200, 201, 404, etc.
  • HTTPException  — how FastAPI returns error responses
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel          # Data validation library
from typing import Optional             # For optional fields
from datetime import datetime, timezone # For timestamps
import uuid                             # For generating unique IDs

from database import read_db, write_db  # Our JSON helper

# ----------------------------------------------------------
# 1. CREATE AN APIRouter
#
#    Think of APIRouter like a "section" of the app.
#    In main.py we do: app.include_router(posts.router)
#    which grafts all these routes onto the main app.
# ----------------------------------------------------------
router = APIRouter()

DB_FILE = "posts.json"   # the JSON file that stores posts

# ----------------------------------------------------------
# 2. PYDANTIC MODELS  (Data Schemas / Validation)
#
#    Pydantic models are Python classes that describe the
#    exact shape of the data we expect to receive or send.
#
#    FastAPI uses them to:
#      • Automatically VALIDATE incoming request bodies
#        (returns 422 Unprocessable Entity if data is wrong)
#      • Automatically GENERATE the /docs schema
#      • Automatically SERIALISE responses to JSON
# ----------------------------------------------------------

class PostCreate(BaseModel):
    """
    Schema for creating a new post.
    The client must send JSON with these two fields.

    Example request body:
        {
            "title": "My First Post",
            "content": "Hello, world!",
            "author": "Alice"
        }
    """
    title:   str            # Required — cannot be omitted
    content: str            # Required
    author:  str            # Required


class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.
    All fields are Optional — the client can send only
    the fields they want to change (PATCH-style update
    via a PUT endpoint).

    Example request body (only updating title):
        { "title": "Updated Title" }
    """
    title:   Optional[str] = None
    content: Optional[str] = None


class Post(BaseModel):
    """
    Schema for a full Post as stored in the DB and
    returned to the client.  Adds id + timestamps.
    """
    id:         str
    title:      str
    content:    str
    author:     str
    created_at: str
    updated_at: str


# ----------------------------------------------------------
# 3. ROUTES
# ----------------------------------------------------------

# ---------- GET /posts  (Read All) ----------
@router.get("/", response_model=list[Post])
def get_all_posts():
    """
    Return every post in the database, newest first.

    FLOW:
      1. Read the JSON file → Python list of dicts
      2. Sort by created_at descending (newest first)
      3. FastAPI serialises the list to JSON automatically
    """
    posts = read_db(DB_FILE)
    # Sort so newest posts appear first
    posts.sort(key=lambda p: p["created_at"], reverse=True)
    return posts


# ---------- GET /posts/{post_id}  (Read One) ----------
@router.get("/{post_id}", response_model=Post)
def get_post(post_id: str):
    """
    Return a single post by its ID.

    PATH PARAMETER:
      FastAPI extracts {post_id} from the URL automatically
      and passes it as the `post_id` argument.

    ERROR HANDLING:
      If no post with that ID exists, we raise HTTPException
      with status 404 (Not Found). FastAPI turns this into
      a proper JSON error response:
          { "detail": "Post not found" }
    """
    posts = read_db(DB_FILE)

    # next() with a default of None is a Pythonic way to search
    post = next((p for p in posts if p["id"] == post_id), None)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id '{post_id}' not found."
        )

    return post


# ---------- POST /posts  (Create) ----------
@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate):
    """
    Create a new forum post.

    REQUEST BODY:
      FastAPI reads the JSON body and validates it against
      the PostCreate schema. If validation fails (e.g. a
      required field is missing), it returns 422 automatically.

    WHAT WE DO:
      1. Build a new dict with auto-generated id + timestamps
      2. Append it to the list loaded from the JSON file
      3. Write the updated list back to the JSON file
      4. Return the newly created post (status 201 Created)

    uuid.uuid4():
      Generates a universally unique identifier — a random
      128-bit number formatted as a hex string. Extremely
      unlikely to ever collide with another ID.

    datetime.now(timezone.utc).isoformat():
      Current time in UTC, formatted as an ISO-8601 string:
      e.g. "2024-07-15T10:30:00+00:00"
    """
    posts = read_db(DB_FILE)

    now = datetime.now(timezone.utc).isoformat()

    new_post = {
        "id":         str(uuid.uuid4()),
        "title":      payload.title,
        "content":    payload.content,
        "author":     payload.author,
        "created_at": now,
        "updated_at": now,
    }

    posts.append(new_post)
    write_db(DB_FILE, posts)

    return new_post


# ---------- PUT /posts/{post_id}  (Update) ----------
@router.put("/{post_id}", response_model=Post)
def update_post(post_id: str, payload: PostUpdate):
    """
    Update the title and/or content of an existing post.

    PARTIAL UPDATE PATTERN:
      payload.model_dump(exclude_unset=True) returns only
      the fields the client actually sent — fields they
      left out are NOT included. This lets the client send:
          { "title": "New Title" }
      without accidentally wiping the content field.

    FLOW:
      1. Load all posts
      2. Find the target post (404 if missing)
      3. Merge in the new field values
      4. Update the updated_at timestamp
      5. Save back to JSON
      6. Return the updated post
    """
    posts = read_db(DB_FILE)

    # Find the index of the post in the list
    idx = next((i for i, p in enumerate(posts) if p["id"] == post_id), None)

    if idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id '{post_id}' not found."
        )

    # Only update fields that were actually sent by the client
    updates = payload.model_dump(exclude_unset=True)
    posts[idx].update(updates)
    posts[idx]["updated_at"] = datetime.now(timezone.utc).isoformat()

    write_db(DB_FILE, posts)

    return posts[idx]


# ---------- DELETE /posts/{post_id}  (Delete) ----------
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str):
    """
    Permanently delete a post (and implicitly its comments
    should be cleaned up — see comments router).

    STATUS 204 No Content:
      By convention, a successful DELETE returns 204 with
      NO response body. The resource is simply gone.

    FLOW:
      1. Load all posts
      2. Filter OUT the post with the matching ID
      3. If the lengths are the same, nothing was removed → 404
      4. Write the filtered list back
    """
    posts = read_db(DB_FILE)
    filtered = [p for p in posts if p["id"] != post_id]

    if len(filtered) == len(posts):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id '{post_id}' not found."
        )

    write_db(DB_FILE, filtered)
    # No return value — 204 means "done, nothing to say"
