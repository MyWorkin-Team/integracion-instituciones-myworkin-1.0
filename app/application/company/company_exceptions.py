class CompanyError(Exception):
    pass

class CompanyUserEmailAlreadyExists(CompanyError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email {email} is already registered in the system.")
