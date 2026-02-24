class CompanyError(Exception):
    pass

class CompanyUserEmailAlreadyExists(CompanyError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"El email {email} ya se encuentra registrado en el sistema.")
