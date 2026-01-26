import json
from fastapi import Path, HTTPException
from app.config.helpers import fail

async def validate_university_id(university_id: str = Path(...)):
    # 1. Tu lista desde el ENV
    allowed = os.getenv("ALLOWED_UNIVERSITIES", "").split(",")
    
    if university_id not in allowed:
        # 2. Generas el error con TU función fail
        error_response = fail(
            code="INVALID_UNIVERSITY",
            message=f"La universidad {university_id} no está permitida",
            status=403
        )
        
        # 3. Lo lanzas para que FastAPI no siga ejecutando el resto del endpoint
        # .body.decode() convierte el contenido de JSONResponse a un diccionario/string
        raise HTTPException(
            status_code=403, 
            detail=json.loads(error_response.body)
        )
    
    return university_id