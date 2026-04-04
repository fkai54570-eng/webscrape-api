from .scrape import router as scrape_router
from .auth import router as auth_router

# 为了兼容 main.py 中的 import
router = scrape_router
