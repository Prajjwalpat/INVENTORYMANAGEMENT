from functools import wraps
from flask import request,jsonify
from config import API_KEY
from logger import logger

def authkey(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key=request.headers.get('x-api-key')
        if not key or key!=API_KEY:
            logger.warning(f"Unauthqrized attempt user: {request.remote_addr}")
            return jsonify({"error":"Unauthqrized"}),401
        return f(*args, **kwargs)
    return decorated