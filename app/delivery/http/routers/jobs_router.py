from fastapi import APIRouter, HTTPException
from rq.job import Job
from rq import Queue
from rq.registry import FinishedJobRegistry, FailedJobRegistry, StartedJobRegistry
from app.infrastructure.queue.redis_client import get_redis_connection
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse
from app.infrastructure.cache.redis_cache import RedisCache

router = APIRouter()


@router.get(
    "/history",
    response_model=ApiResponse[dict]
)
async def get_jobs_history():
    """Get history of completed and failed jobs"""
    try:
        conn = get_redis_connection()
        queue_names = ["students", "companies"]

        history_data = {
            "completed": [],
            "failed": [],
            "processing": []
        }

        for queue_name in queue_names:
            q = Queue(queue_name, connection=conn)

            # Completed jobs
            finished_registry = FinishedJobRegistry(queue=q, connection=conn)
            for job_id in finished_registry.get_job_ids()[-20:]:  # Last 20
                try:
                    job = Job.fetch(job_id, connection=conn)
                    history_data["completed"].append({
                        "job_id": job.id,
                        "queue": queue_name,
                        "status": "finished",
                        "result": str(job.result) if job.result else None,
                        "ended_at": str(job.ended_at) if job.ended_at else None,
                    })
                except:
                    pass

            # Failed jobs
            failed_registry = FailedJobRegistry(queue=q, connection=conn)
            for job_id in failed_registry.get_job_ids()[-20:]:  # Last 20
                try:
                    job = Job.fetch(job_id, connection=conn)
                    history_data["failed"].append({
                        "job_id": job.id,
                        "queue": queue_name,
                        "status": "failed",
                        "exc_info": job.exc_info[:200] if job.exc_info else None,
                        "ended_at": str(job.ended_at) if job.ended_at else None,
                    })
                except:
                    pass

            # Currently processing
            started_registry = StartedJobRegistry(queue=q, connection=conn)
            for job_id in started_registry.get_job_ids():
                try:
                    job = Job.fetch(job_id, connection=conn)
                    history_data["processing"].append({
                        "job_id": job.id,
                        "queue": queue_name,
                        "status": "processing",
                        "started_at": str(job.started_at) if job.started_at else None,
                    })
                except:
                    pass

        return ok(
            status=200,
            result="success",
            message="Historial de jobs",
            data=history_data
        )
    except Exception as e:
        return fail(
            status=500,
            code="HISTORY_ERROR",
            message=f"Error al consultar historial: {str(e)}"
        )


@router.get(
    "/queues",
    response_model=ApiResponse[dict]
)
async def get_queues():
    """List all queues and their job counts"""
    try:
        conn = get_redis_connection()
        queue_names = ["students", "companies"]

        queues_data = []
        total_jobs = 0

        for queue_name in queue_names:
            q = Queue(queue_name, connection=conn)
            job_ids = q.job_ids
            queued_count = len(job_ids)
            total_jobs += queued_count

            queues_data.append({
                "name": queue_name,
                "count": queued_count,
                "jobs": job_ids[:20]  # Show first 20 job IDs
            })

        return ok(
            status=200,
            result="success",
            message=f"Total de {total_jobs} jobs en cola",
            data={
                "total_jobs": total_jobs,
                "queues": queues_data
            }
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error al consultar colas: {str(e)}"
        )


@router.get(
    "/queues/{queue_name}",
    response_model=ApiResponse[dict]
)
async def get_queue_details(queue_name: str):
    """Get detailed info about a specific queue"""
    try:
        if queue_name not in ["students", "companies"]:
            return fail(
                status=400,
                code="INVALID_QUEUE",
                message=f"Cola '{queue_name}' no existe. Usa 'students' o 'companies'"
            )

        conn = get_redis_connection()
        q = Queue(queue_name, connection=conn)
        job_ids = q.job_ids

        jobs_data = []
        for job_id in job_ids:
            try:
                job = Job.fetch(job_id, connection=conn)
                jobs_data.append({
                    "job_id": job.id,
                    "status": job.get_status(),
                    "func_name": job.func_name if hasattr(job, 'func_name') else "unknown",
                    "created_at": str(job.created_at) if job.created_at else None,
                })
            except:
                pass

        return ok(
            status=200,
            result="success",
            message=f"Cola '{queue_name}' contiene {len(job_ids)} jobs",
            data={
                "queue_name": queue_name,
                "total_jobs": len(job_ids),
                "jobs": jobs_data
            }
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error: {str(e)}"
        )


@router.delete(
    "/queues",
    response_model=ApiResponse[dict]
)
async def clear_all_queues():
    """Clear all jobs from all queues AND history"""
    try:
        conn = get_redis_connection()
        queue_names = ["students", "companies"]
        total_deleted = 0

        for queue_name in queue_names:
            q = Queue(queue_name, connection=conn)

            # Clear active jobs
            job_count = len(q.job_ids)
            total_deleted += job_count
            q.empty()

            # Clear history registries
            finished_registry = FinishedJobRegistry(queue=q, connection=conn)
            failed_registry = FailedJobRegistry(queue=q, connection=conn)
            started_registry = StartedJobRegistry(queue=q, connection=conn)

            for job_id in finished_registry.get_job_ids():
                finished_registry.remove(job_id)
                total_deleted += 1

            for job_id in failed_registry.get_job_ids():
                failed_registry.remove(job_id)
                total_deleted += 1

            for job_id in started_registry.get_job_ids():
                started_registry.remove(job_id)
                total_deleted += 1

        return ok(
            status=200,
            result="cleared",
            message="Todas las colas e historial vaciados exitosamente",
            data={
                "total_jobs_deleted": total_deleted,
                "queues_cleared": queue_names
            }
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error al limpiar colas: {str(e)}"
        )


@router.delete(
    "/history",
    response_model=ApiResponse[dict]
)
async def clear_history():
    """Clear job history (completed, failed, processing)"""
    try:
        conn = get_redis_connection()
        queue_names = ["students", "companies"]
        total_deleted = 0

        for queue_name in queue_names:
            q = Queue(queue_name, connection=conn)

            finished_registry = FinishedJobRegistry(queue=q, connection=conn)
            failed_registry = FailedJobRegistry(queue=q, connection=conn)
            started_registry = StartedJobRegistry(queue=q, connection=conn)

            for job_id in finished_registry.get_job_ids():
                finished_registry.remove(job_id)
                total_deleted += 1

            for job_id in failed_registry.get_job_ids():
                failed_registry.remove(job_id)
                total_deleted += 1

            for job_id in started_registry.get_job_ids():
                started_registry.remove(job_id)
                total_deleted += 1

        return ok(
            status=200,
            result="cleared",
            message="Historial limpiado exitosamente",
            data={
                "total_jobs_deleted": total_deleted,
                "queues_affected": queue_names
            }
        )
    except Exception as e:
        return fail(
            status=500,
            code="HISTORY_ERROR",
            message=f"Error al limpiar historial: {str(e)}"
        )


@router.delete(
    "/queues/{queue_name}",
    response_model=ApiResponse[dict]
)
async def clear_queue(queue_name: str):
    """Clear all jobs from a queue"""
    try:
        if queue_name not in ["students", "companies"]:
            return fail(
                status=400,
                code="INVALID_QUEUE",
                message=f"Cola '{queue_name}' no existe. Usa 'students' o 'companies'"
            )

        conn = get_redis_connection()
        q = Queue(queue_name, connection=conn)
        job_count = len(q.job_ids)
        q.empty()

        return ok(
            status=200,
            result="cleared",
            message=f"Cola '{queue_name}' vaciada exitosamente",
            data={
                "queue_name": queue_name,
                "jobs_deleted": job_count
            }
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error al limpiar cola: {str(e)}"
        )


@router.delete(
    "/{job_id}",
    response_model=ApiResponse[dict]
)
async def delete_job(job_id: str):
    """Delete a specific job"""
    try:
        conn = get_redis_connection()
        job = Job.fetch(job_id, connection=conn)
        job.delete()

        return ok(
            status=200,
            result="deleted",
            message=f"Job '{job_id}' eliminado exitosamente",
            data={"job_id": job_id}
        )
    except Exception as e:
        return fail(
            status=404,
            code="JOB_NOT_FOUND",
            message=f"Job no encontrado: {str(e)}"
        )


@router.get(
    "/{job_id}",
    response_model=ApiResponse[dict]
)
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    try:
        conn = get_redis_connection()
        job = Job.fetch(job_id, connection=conn)

        data = {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "exc_info": job.exc_info if job.is_failed else None,
        }

        if job.is_finished:
            return ok(
                status=200,
                result="finished",
                message="Job completado exitosamente",
                data=data
            )
        elif job.is_failed:
            return ok(
                status=200,
                result="failed",
                message="Job falló",
                data=data
            )
        else:
            return ok(
                status=200,
                result="processing",
                message=f"Job en estado: {job.get_status()}",
                data=data
            )

    except Exception as e:
        return fail(
            status=404,
            code="JOB_NOT_FOUND",
            message=f"No se encontró el job: {str(e)}"
        )


@router.get(
    "/cache/entities",
    response_model=ApiResponse[dict]
)
async def get_cached_entities():
    """Get all cached entity keys (format: university_id:identifier:email)"""
    try:
        conn = get_redis_connection()
        entities_data = {
            "students": [],
            "companies": []
        }

        # Get all student keys (excluding :data suffix)
        for key in conn.scan_iter(match=f"{RedisCache.STUDENT_PREFIX}*"):
            key_str = key.decode() if isinstance(key, bytes) else key
            # Exclude :data keys, only show main keys
            if not key_str.endswith(":data"):
                entities_data["students"].append(key_str)

        # Get all company keys (excluding :data suffix)
        for key in conn.scan_iter(match=f"{RedisCache.COMPANY_PREFIX}*"):
            key_str = key.decode() if isinstance(key, bytes) else key
            # Exclude :data keys, only show main keys
            if not key_str.endswith(":data"):
                entities_data["companies"].append(key_str)

        total = len(entities_data["students"]) + len(entities_data["companies"])
        return ok(
            status=200,
            result="success",
            message=f"Total: {total} cached entities",
            data=entities_data
        )
    except Exception as e:
        return fail(
            status=500,
            code="CACHE_ERROR",
            message=f"Error al consultar datos: {str(e)}"
        )


@router.delete(
    "/cache/entities",
    response_model=ApiResponse[dict]
)
async def clear_cached_entities():
    """Clear all cached entities"""
    try:
        RedisCache.clear_cache()
        return ok(
            status=200,
            result="cleared",
            message="All cached entities cleared successfully",
            data={"status": "cleared"}
        )
    except Exception as e:
        return fail(
            status=500,
            code="CACHE_ERROR",
            message=f"Error al limpiar datos: {str(e)}"
        )
