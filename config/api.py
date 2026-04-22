from ninja import NinjaAPI

from config.admin_api import router as admin_router
from catalog.api import router as catalog_router
from orders.api import router as orders_router
from users.api import router as users_router

api = NinjaAPI(title="Fenix API", version="1.0.0")
# Health check
@api.get("/health", tags=["health"])
def health(request):
    return {"status": "ok"}
api.add_router("/catalog", catalog_router)
api.add_router("/orders", orders_router)
api.add_router("/users/", users_router)
api.add_router("/admin", admin_router)
