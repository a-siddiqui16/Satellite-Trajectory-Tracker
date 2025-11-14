import bcrypt

#Function to hash password
def hash_password(password):

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    hashed_password = hashed.decode('utf-8')
    return hashed_password

print(hash_password(password="helloess"))