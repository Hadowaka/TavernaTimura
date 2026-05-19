"""
============================================================
  main.py  —  FastAPI Forum Application Entry Point
============================================================

WHAT THIS FILE DOES:
  This is the "heart" of the application. It creates the
  FastAPI app instance, registers routers (sub-applications
  that handle specific URL groups), and configures CORS so
  that our browser-based frontend can talk to the API.

KEY CONCEPTS EXPLAINED HERE:
  • FastAPI()          — creates the web application
  • app.include_router() — plugs in route modules
  • CORSMiddleware    — allows cross-origin HTTP requests
  • @app.get("/")     — a simple health-check route
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our two routers (defined in the routers/ folder)
from routers import posts, comments

# ----------------------------------------------------------
# 1. CREATE THE FASTAPI APPLICATION INSTANCE
#    Think of `app` as the central hub. Every route, every
#    middleware, and every configuration is attached to it.
# ----------------------------------------------------------
app = FastAPI(
    title="Simple Forum API",
    description="A learning project: Forum API backed by JSON files instead of a real DB.",
    version="1.0.0"
)

# ----------------------------------------------------------
# 2. CORS — Cross-Origin Resource Sharing
#
#    Browsers block requests from one "origin" (domain+port)
#    to another by default. Since our HTML file is opened
#    directly in a browser (or served from a different port),
#    we must tell FastAPI to allow those requests.
#
#    allow_origins=["*"]  →  accept requests from ANY origin
#    allow_methods=["*"]  →  accept GET, POST, PUT, DELETE …
#    allow_headers=["*"]  →  accept any HTTP header
#
#    ⚠️  In production you would restrict this to your exact
#    frontend domain instead of "*".
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# 3. REGISTER ROUTERS
#
#    Instead of defining every route in this single file,
#    we split them into separate modules (routers/posts.py
#    and routers/comments.py).
#
#    include_router() merges those routes into the main app.
#
#    prefix="/posts"    → all routes inside posts.py will
#                         start with /posts
#    tags=["Posts"]     → groups them nicely in the
#                         auto-generated /docs page
# ----------------------------------------------------------
app.include_router(posts.router,    prefix="/posts",    tags=["Posts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])

# ----------------------------------------------------------
# 4. ROOT HEALTH-CHECK ENDPOINT
#
#    A simple GET / route. Useful to quickly verify the
#    server is running. Returns a plain JSON message.
# ----------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    return {"message": "Forum API is running! Visit /docs for the interactive documentation."}


# ----------------------------------------------------------
# 5. HOW TO RUN THIS APPLICATION
#
#    From your terminal (inside the project folder):
#
#       pip install fastapi uvicorn
#       uvicorn main:app --reload
#
#    • `main`   → the filename (main.py)
#    • `app`    → the FastAPI instance inside that file
#    • --reload → auto-restarts when you save changes
#
#    Then open:
#      http://127.0.0.1:8000/docs   ← Swagger UI (interactive)
#      http://127.0.0.1:8000/redoc  ← ReDoc (readable docs)
# ----------------------------------------------------------
