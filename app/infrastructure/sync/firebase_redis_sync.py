import logging
from app.infrastructure.queue.redis_client import get_redis_connection
from app.infrastructure.cache.redis_cache import RedisCache
from app.config.di_student import init_firebase as init_firebase_student
from app.config.di_company import init_firebase as init_firebase_company

logger = logging.getLogger(__name__)


def sync_firebase_to_redis(university_id: str):
    """Sync all students and companies from Firebase to Redis cache"""
    try:
        logger.info(f"Starting Firebase→Redis sync for {university_id}")

        # Sync students
        try:
            app = init_firebase_student(university_id)
            db = app.firestore()
            students_ref = db.collection("universities").document(university_id).collection("students")

            student_count = 0
            for doc in students_ref.stream():
                try:
                    student_data = doc.to_dict()
                    dni = student_data.get("dni")
                    email = student_data.get("email", "")

                    if dni:
                        cache_data = {
                            "university_id": university_id,
                            "dni": dni,
                            "email": email,
                            "displayName": student_data.get("displayName"),
                            "career": student_data.get("career"),
                            "studentStatus": student_data.get("studentStatus"),
                            "createdAt": str(student_data.get("createdAt")) if student_data.get("createdAt") else None,
                            "updatedAt": str(student_data.get("updatedAt")) if student_data.get("updatedAt") else None,
                        }
                        RedisCache.register_student(dni, email, university_id, cache_data)
                        student_count += 1
                except Exception as e:
                    logger.error(f"Error syncing student {doc.id}: {str(e)}")

            logger.info(f"✓ Synced {student_count} students for {university_id}")
        except Exception as e:
            logger.error(f"Error syncing students for {university_id}: {str(e)}")

        # Sync companies
        try:
            app = init_firebase_company(university_id)
            db = app.firestore()
            companies_ref = db.collection("universities").document(university_id).collection("companies")

            company_count = 0
            for doc in companies_ref.stream():
                try:
                    company_data = doc.to_dict()
                    ruc = company_data.get("ruc")

                    if ruc:
                        # Get first email from users_companies
                        company_email = ""
                        users_data = []
                        if company_data.get("users_companies"):
                            for user in company_data["users_companies"]:
                                if user.get("email") and not company_email:
                                    company_email = user["email"]
                                users_data.append({
                                    "email": user.get("email"),
                                    "firstName": user.get("firstName"),
                                    "lastName": user.get("lastName")
                                })

                        cache_data = {
                            "university_id": university_id,
                            "ruc": ruc,
                            "displayName": company_data.get("displayName"),
                            "sector": company_data.get("sector"),
                            "phone": company_data.get("phone"),
                            "users_companies": users_data,
                            "createdAt": str(company_data.get("createdAt")) if company_data.get("createdAt") else None,
                            "updatedAt": str(company_data.get("updatedAt")) if company_data.get("updatedAt") else None,
                        }
                        RedisCache.register_company(ruc, company_email, university_id, cache_data)
                        company_count += 1
                except Exception as e:
                    logger.error(f"Error syncing company {doc.id}: {str(e)}")

            logger.info(f"✓ Synced {company_count} companies for {university_id}")
        except Exception as e:
            logger.error(f"Error syncing companies for {university_id}: {str(e)}")

        logger.info(f"✓ Firebase→Redis sync completed for {university_id}")
    except Exception as e:
        logger.error(f"Critical error during Firebase→Redis sync: {str(e)}")


def sync_all_universities():
    """Sync all configured universities from Firebase to Redis"""
    # Get list of universities from environment or config
    universities = ["UNT", "UTEST"]  # TODO: Load from config/env

    logger.info(f"Starting Firebase→Redis sync for all universities: {universities}")

    for university_id in universities:
        try:
            sync_firebase_to_redis(university_id)
        except Exception as e:
            logger.error(f"Error syncing university {university_id}: {str(e)}")

    logger.info("Firebase→Redis sync completed for all universities")
