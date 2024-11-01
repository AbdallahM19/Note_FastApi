"""session.py"""

from fastapi import Request


class SessionManager:
    """Session manager for FastAPI."""
    def __init__(self, request: Request):
        self.request = request

    def get_session_id(self) -> str:
        """Get session id from session object."""
        return self.request.session.get("session_id")

    def set_session_id(self, session_id: str):
        """Set session id in session object."""
        self.request.session["session_id"] = session_id

    def clear_session(self):
        """Clear session object."""
        self.request.session.clear()

def get_session_manager(request: Request) -> SessionManager:
    """Get session manager instance from request."""
    return SessionManager(request)
