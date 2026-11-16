from datetime import datetime
from paseos.app import app
from paseos.core.dependencies import get_ahora

app.dependency_overrides[get_ahora] = lambda: datetime(2026, 5, 10, 10, 0)