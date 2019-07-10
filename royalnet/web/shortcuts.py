import flask as f
import uuid as _uuid
import base64


def error(code, reason):
    return f.render_template("error.html", title=f"Errore {code}", reason=reason), code


def to_urluuid(uuid: _uuid.UUID) -> str:
    """Return a base64 url-friendly short UUID."""
    return str(base64.urlsafe_b64encode(uuid.bytes), encoding="ascii")


def from_urluuid(b: str) -> _uuid.UUID:
    return _uuid.UUID(bytes=base64.urlsafe_b64decode(bytes(b, encoding="ascii")))
