"""
Server entry point for supervisor compatibility
This file imports the FastAPI app from main.py
"""
from main import app

__all__ = ["app"]
