"""session.py"""

from fastapi import Request


def get_session(request: Request) -> dict:
    """Get the session from the request."""
    return request.session

def set_session(request: Request, **kwargs):
    """Set the session from the request."""
    request.session.update(**kwargs)

def clear_session(request: Request):
    """Clear the session data."""
    request.session.clear()
