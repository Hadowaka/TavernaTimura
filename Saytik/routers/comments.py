"""
============================================================
  routers/comments.py  —  All Forum Comment Endpoints
============================================================

WHAT THIS FILE DOES:
  Defines every HTTP route that deals with COMMENTS on posts:
    GET    /comments/post/{post_id}  → list all comments on a post
    POST   /comments/post/{post_id}  → add a comment to a post
    DELETE /comments/{comment_id}    → delete a single comment

  Comments are stored in data/comments.json and each comment
  has a `post_id` field linking it to its parent post.

KEY CONCEPTS (new ones compared to posts.py):
  • Foreign key simulation  — post_id links comment → post
  • Cross-router validation — we read posts.json inside the
    comments router to verify the post exists before adding
    a comment (referential integrity, manually enforced)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

from database import read_db, write_db

router = APIRouter()

COMMENTS_FILE = "comments.json"
POSTS_FILE    = "posts.json"


# ----------------------------------------------------------
# PYDANTIC MODELS
# ----------------------------------------------------------

class CommentCreate(BaseModel):
    """
    Schema for creating a comment.

    Example request body:
        {
            "content": "Great post, thanks!",
            "author": "Bob"
        }

    Notice: `post_id` is NOT in this schema because it comes
    from the URL path parameter instead — a cleaner design.
    """
    content: str
    author:  str


class Comment(BaseModel):
    """Full comment as stored and returned."""
    id:         str
    post_id:    str       # Which post this comment belongs to
    content:    str
    author:     str
    created_at: str


# ----------------------------------------------------------
# ROUTES
# ----------------------------------------------------------

# ---------- GET /comments/post/{post_id}  (Read All for a Post) ----------
@router.get("/post/{post_id}", response_model=list[Comment])
def get_comments_for_post(post_id: str):
    """
    Return all comments that belong to a specific post.

    FOREIGN KEY PATTERN:
      Each comment dict has a "post_id" field. We filter the
      entire comments list to only return the ones matching.
      In a real database this would be a WHERE clause:
          SELECT * FROM comments WHERE post_id = ?

    VALIDATION:
      We first check if the post actually exists.
      If not → 404, to prevent returning comments for a
      ghost post (one that was deleted).
    """
    # Verify the parent post exists
    posts = read_db(POSTS_FILE)
    post_exists = any(p["id"] == post_id for p in posts)

    if not post_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id '{post_id}' not found."
        )

    # Filter comments by post_id
    comments = read_db(COMMENTS_FILE)
    post_comments = [c for c in comments if c["post_id"] == post_id]

    # Sort oldest-first (natural reading order for a thread)
    post_comments.sort(key=lambda c: c["created_at"])

    return post_comments


# ---------- POST /comments/post/{post_id}  (Create) ----------
@router.post(
    "/post/{post_id}",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED
)
def create_comment(post_id: str, payload: CommentCreate):
    """
    Add a new comment to a specific post.

    REFERENTIAL INTEGRITY (manual):
      Before inserting, we check that the referenced post
      actually exists in posts.json. A real relational DB
      would enforce this automatically via a FOREIGN KEY
      constraint. Here we do it by hand.

    FLOW:
      1. Verify post exists → 404 if not
      2. Build new comment dict
      3. Append to comments list
      4. Save back to comments.json
      5. Return the new comment (201 Created)
    """
    # Check parent post exists
    posts = read_db(POSTS_FILE)
    if not any(p["id"] == post_id for p in posts):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot comment: post '{post_id}' does not exist."
        )

    comments = read_db(COMMENTS_FILE)

    new_comment = {
        "id":         str(uuid.uuid4()),
        "post_id":    post_id,
        "content":    payload.content,
        "author":     payload.author,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    comments.append(new_comment)
    write_db(COMMENTS_FILE, comments)

    return new_comment


# ---------- DELETE /comments/{comment_id}  (Delete) ----------
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: str):
    """
    Delete a single comment by its ID.

    Same pattern as deleting a post:
      filter it out → if list length unchanged → 404
      otherwise → save and return 204
    """
    comments = read_db(COMMENTS_FILE)
    filtered = [c for c in comments if c["id"] != comment_id]

    if len(filtered) == len(comments):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id '{comment_id}' not found."
        )

    write_db(COMMENTS_FILE, filtered)


# ---------- BONUS: DELETE all comments for a post ----------
@router.delete("/post/{post_id}/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_comments_for_post(post_id: str):
    """
    Delete every comment belonging to a post.

    WHEN IS THIS USEFUL?
      When a post is deleted, its comments become orphans
      (they reference a post_id that no longer exists).
      The frontend can call this endpoint after deleting a
      post to clean up. In a real DB you'd use ON DELETE CASCADE.
    """
    comments = read_db(COMMENTS_FILE)
    filtered = [c for c in comments if c["post_id"] != post_id]
    write_db(COMMENTS_FILE, filtered)
