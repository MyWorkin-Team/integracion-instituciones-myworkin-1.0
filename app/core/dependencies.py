from typing import Optional
from fastapi import Path, HTTPException, Request
import json
import os
from app.config.helpers import fail

async def validate_university_id(request: Request, university_id: Optional[str] = None):
    # Si no viene por el path (university_id es None), intentamos leerlo del body
    if university_id is None:
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.json()
                university_id = body.get("university_id")
            except Exception:
                university_id = None
        else:
            # Para otros métodos (GET), intentamos buscarlo en los path_params si no se inyectó automáticamente
            university_id = request.path_params.get("university_id")

    if not university_id:
        error_response = fail(
            code="MISSING_UNIVERSITY",
            message="university_id is required in body or path",
            status=400
        )
        raise HTTPException(
            status_code=400,
            detail=json.loads(error_response.body)
        )

    # 1. Tu lista desde el ENV
    allowed = os.getenv("ALLOWED_UNIVERSITIES", "").split(",")
    # Limpiar espacios en blanco de cada elemento de la lista
    allowed = [u.strip().upper() for u in allowed if u.strip()]
    
    university_id_upper = university_id.upper()
    
    if university_id_upper not in allowed:
        # 2. Generas el error con TU función fail
        error_response = fail(
            code="INVALID_UNIVERSITY",
            message=f"University {university_id} is not allowed",
            status=403
        )
        
        # 3. Lo lanzas
        raise HTTPException(
            status_code=403, 
            detail=json.loads(error_response.body)
        )
    
    return university_id
