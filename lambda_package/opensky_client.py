import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import time
import os

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
CLIENT_ID = os.getenv("OPENSKY_CLIENT_ID")
CLIENT_SECRET = os.getenv("OPENSKY_CLIENT_SECRET")
TOKEN_REFRESH_MARGIN = 30

class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = None

    def get_token(self):
        if self.token and self.expires_at and datetime.now() < self.expires_at:
            return self.token
        return self._refresh()

    def _refresh(self):
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }).encode()

        req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())

        self.token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_REFRESH_MARGIN)
        return self.token

    def headers(self):
        return {"Authorization": f"Bearer {self.get_token()}"}