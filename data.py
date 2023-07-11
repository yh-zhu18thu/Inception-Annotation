def validate_user(id,password):
    if id=='admin' and password=='admin':
        return True
    else:
        return False