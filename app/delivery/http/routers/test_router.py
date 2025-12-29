from fastapi import APIRouter

router = APIRouter()

@router.get("/route-test")
async def test_route():
    return {
        "status": "ok",
        "message": "Route is working correctly"
    }
