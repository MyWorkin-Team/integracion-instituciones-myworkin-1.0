import logging
import os
from app.config.di_student import init_firebase as init_firebase_student
from app.config.di_company import init_firebase as init_firebase_company

logger = logging.getLogger(__name__)


def get_configured_universities() -> list[str]:
    """Get list of configured universities from environment"""
    universities_str = os.getenv("CONFIGURED_UNIVERSITIES", "UNT,UTEST")
    return [uni.strip() for uni in universities_str.split(",") if uni.strip()]


class FirebaseValidator:
    """Validate entities against Firebase (authority source) - Global validation"""

    @staticmethod
    def email_exists_globally(email: str) -> tuple[bool, str]:
        """Check if email exists globally (any university, any entity type)
        Returns: (exists, entity_type) where entity_type is 'student', 'company', or None
        """
        email_lower = email.lower()
        universities = get_configured_universities()

        # Check all universities for students
        for uni in universities:
            try:
                app = init_firebase_student(uni)
                db = app.firestore()
                students_ref = db.collection("universities").document(uni).collection("students")
                query = students_ref.where("email", "==", email_lower)
                if any(query.stream()):
                    return True, "student"
            except Exception as e:
                logger.debug(f"Error checking student email in {uni}: {str(e)}")

        # Check all universities for companies
        for uni in universities:
            try:
                app = init_firebase_company(uni)
                db = app.firestore()
                companies_ref = db.collection("universities").document(uni).collection("companies")

                docs = companies_ref.stream()
                for doc in docs:
                    company_data = doc.to_dict()
                    if company_data.get("users_companies"):
                        for user in company_data["users_companies"]:
                            if user.get("email", "").lower() == email_lower:
                                return True, "company"
            except Exception as e:
                logger.debug(f"Error checking company email in {uni}: {str(e)}")

        return False, None

    @staticmethod
    def student_dni_exists(dni: str, university_id: str) -> bool:
        """Check if student DNI exists in Firebase for specific university"""
        try:
            app = init_firebase_student(university_id)
            db = app.firestore()
            students_ref = db.collection("universities").document(university_id).collection("students")

            query = students_ref.where("dni", "==", dni)
            return any(query.stream())
        except Exception as e:
            logger.error(f"Error validating student DNI in Firebase: {str(e)}")
            return False

    @staticmethod
    def company_ruc_exists(ruc: str, university_id: str) -> bool:
        """Check if company RUC exists in Firebase for specific university"""
        try:
            app = init_firebase_company(university_id)
            db = app.firestore()
            companies_ref = db.collection("universities").document(university_id).collection("companies")

            query = companies_ref.where("ruc", "==", ruc)
            return any(query.stream())
        except Exception as e:
            logger.error(f"Error validating company RUC in Firebase: {str(e)}")
            return False
