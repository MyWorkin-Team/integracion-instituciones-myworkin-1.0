class FirebaseError(Exception):
    pass

class FirebaseUserNotFound(FirebaseError):
    pass

class FirebaseUserAlreadyExists(FirebaseError):
    pass

class FirebaseUserCreateError(FirebaseError):
    pass

class FirebaseUserUpdateError(FirebaseError):
    pass
