#!/usr/bin/env python3
"""
Twitter clone backend API entry point.

Exposes REST endpoints for post retrieval, post creation, and authentication.
This is the system under test (SUT) for the pytest-framework.
"""

from fastapi import FastAPI

APP_VERSION = "0.1.0"

app = FastAPI(title="Twitter Clone API", version=APP_VERSION)


@app.get("/health")
async def health_check():
    """Returns service health status."""
    return {"status": "healthy", "version": APP_VERSION}


@app.get("/posts")
async def get_posts():
    """
    Returns all posts, newest first. No authentication required.

    Returns:
        JSON array of post objects.
    """
    # TODO: implement SQLite retrieval
    return []


@app.post("/posts", status_code=201)
async def create_post():
    """
    Creates a new post. Requires authentication.

    Returns:
        The created post object, or an error.
    """
    # TODO: implement auth check, validation (256 char, non-whitespace,
    #       10-second duplicate rule), SQLite storage
    return {"error": "not implemented"}


@app.post("/auth/login")
async def login():
    """
    Authenticates a user and returns a JWT.

    Returns:
        JSON with the access token, or an error.
    """
    # TODO: implement credential validation, JWT issuance
    return {"error": "not implemented"}
