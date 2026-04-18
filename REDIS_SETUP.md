# Redis Queue Implementation

## Configuración e Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Variables de entorno
Agregar a tu `.env`:
```
REDIS_URL=redis://localhost:6379
```

## Ejecutar el sistema

### Terminal 1: Redis (si no está en Docker)
```bash
# Opción 1: Docker
docker run -d -p 6379:6379 redis:7

# Opción 2: Instalado localmente
redis-server
```

### Terminal 2: FastAPI
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: RQ Worker
```bash
python worker.py
```

## Uso de la API

### Encolar un estudiante
```bash
curl -X POST http://localhost:8000/api/students/push \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_API_KEY" \
  -d '{
    "university_id": "UTEST",
    "dni": "12345678",
    "email": "student@example.com",
    "displayName": "John Doe",
    "career": "Ingeniería",
    "studentStatus": "Estudiante"
  }'
```

**Respuesta (202 Accepted):**
```json
{
  "status": 202,
  "label": "Accepted",
  "body": {
    "result": "queued",
    "message": "Estudiante encolado para procesamiento",
    "data": {
      "job_id": "abcd1234-efgh-5678-ijkl-9012mnop",
      "dni": "12345678"
    }
  }
}
```

### Encolar una empresa
```bash
curl -X POST http://localhost:8000/api/companies/push \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_API_KEY" \
  -d '{
    "university_id": "UTEST",
    "ruc": "20123456789",
    "displayName": "TechCorp",
    "sector": "Tecnología",
    "phone": "+51987654321",
    "users_companies": [
      {
        "email": "contact@techcorp.com",
        "firstName": "Juan",
        "lastName": "Pérez"
      }
    ]
  }'
```

### Ver historial de jobs (completados, fallidos, procesando)
```bash
curl http://localhost:8000/api/history
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "success",
    "message": "Historial de jobs",
    "data": {
      "completed": [
        {
          "job_id": "abc-123",
          "queue": "students",
          "status": "finished",
          "result": "created",
          "ended_at": "2026-04-17 18:09:03.123456"
        }
      ],
      "failed": [
        {
          "job_id": "xyz-789",
          "queue": "companies",
          "status": "failed",
          "exc_info": "FirebaseConfigError: La configuración...",
          "ended_at": "2026-04-17 18:05:00.000000"
        }
      ],
      "processing": [
        {
          "job_id": "def-456",
          "queue": "students",
          "status": "processing",
          "started_at": "2026-04-17 18:09:10.000000"
        }
      ]
    }
  }
}
```

### Ver todas las colas (activas)
```bash
curl http://localhost:8000/api/queues
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "success",
    "message": "Total de 5 jobs en cola",
    "data": {
      "total_jobs": 5,
      "queues": [
        {
          "name": "students",
          "count": 3,
          "jobs": ["job-1", "job-2", "job-3"]
        },
        {
          "name": "companies",
          "count": 2,
          "jobs": ["job-4", "job-5"]
        }
      ]
    }
  }
}
```

### Ver detalles de una cola específica
```bash
curl http://localhost:8000/api/queues/students
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "success",
    "message": "Cola 'students' contiene 3 jobs",
    "data": {
      "queue_name": "students",
      "total_jobs": 3,
      "jobs": [
        {
          "job_id": "abcd1234",
          "status": "queued",
          "func_name": "app.workers.student_tasks.upsert_student_job",
          "created_at": "2026-04-17 18:03:11.123456"
        }
      ]
    }
  }
}
```

### Limpiar TODAS las colas + historial
```bash
curl -X DELETE http://localhost:8000/api/queues
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "cleared",
    "message": "Todas las colas e historial vaciados exitosamente",
    "data": {
      "total_jobs_deleted": 5,
      "queues_cleared": ["students", "companies"]
    }
  }
}
```

### Limpiar solo el historial (completados + fallidos)
```bash
curl -X DELETE http://localhost:8000/api/history
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "cleared",
    "message": "Historial limpiado exitosamente",
    "data": {
      "total_jobs_deleted": 42,
      "queues_affected": ["students", "companies"]
    }
  }
}
```

### Limpiar una cola específica
```bash
curl -X DELETE http://localhost:8000/api/queues/students
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "cleared",
    "message": "Cola 'students' vaciada exitosamente",
    "data": {
      "queue_name": "students",
      "jobs_deleted": 3
    }
  }
}
```

### Consultar estado de un job específico
```bash
curl http://localhost:8000/api/jobs/abcd1234-efgh-5678-ijkl-9012mnop
```

**Respuesta (mientras se procesa):**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "processing",
    "message": "Job en estado: started",
    "data": {
      "job_id": "abcd1234-efgh-5678-ijkl-9012mnop",
      "status": "started",
      "result": null,
      "exc_info": null
    }
  }
}
```

**Respuesta (completado):**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "finished",
    "message": "Job completado exitosamente",
    "data": {
      "job_id": "abcd1234-efgh-5678-ijkl-9012mnop",
      "status": "finished",
      "result": "created",
      "exc_info": null
    }
  }
}
```

### Eliminar un job específico
```bash
curl -X DELETE http://localhost:8000/api/jobs/abcd1234-efgh-5678-ijkl-9012mnop
```

**Respuesta:**
```json
{
  "status": 200,
  "label": "OK",
  "body": {
    "result": "deleted",
    "message": "Job 'abcd1234-efgh-5678-ijkl-9012mnop' eliminado exitosamente",
    "data": {
      "job_id": "abcd1234-efgh-5678-ijkl-9012mnop"
    }
  }
}
```

## Flujo de Operación

### Sin RQ (Anterior)
```
POST /students/push 
  → Valida university_id 
  → Ejecuta Firebase Auth calls ⏳
  → Ejecuta Firestore writes ⏳
  → Devuelve 200/201 (lento)
```

### Con RQ (Actual)
```
POST /students/push 
  → Valida university_id 
  → Encola job en Redis ⚡
  → Devuelve 202 con job_id ⚡
  
Worker RQ (en background):
  → Procesa job
  → Ejecuta Firebase Auth calls ⏳
  → Ejecuta Firestore writes ⏳
  → Almacena resultado en Redis
```

## Beneficios

- ✅ **API rápida**: `/push` devuelve respuesta inmediata (202)
- ✅ **Sin bloqueos**: Múltiples requests no se bloquean entre sí
- ✅ **Escalable**: Puedes iniciar múltiples workers
- ✅ **Confiable**: Los jobs persisten en Redis hasta completarse
- ✅ **Monitoreable**: Puedes consultar estado de cada job

## Problemas y Soluciones

| Problema | Solución |
|----------|----------|
| "Could not connect to Redis" | Verifica que Redis está corriendo en `REDIS_URL` |
| Worker se queda vacío | Verifica que las colas están correctas en `worker.py` |
| Job falla con "Module not found" | Asegúrate de ejecutar worker desde la raíz del proyecto |
| Job se congela | Aumenta timeout en `Queue.enqueue(..., job_timeout='5m')` |

## Logs del Worker

El worker muestra logs de qué está procesando:

```
14:32:10 Worker rq:worker:...
14:32:15 Job 'app.workers.student_tasks.upsert_student_job' started
14:32:18 Job 'app.workers.student_tasks.upsert_student_job' ended with result 'created'
```

## Docker Compose (Opcional)

Para ambiente de producción:

```yaml
version: '3.8'
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0

  worker:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    command: python worker.py
```

```bash
docker-compose up
```
