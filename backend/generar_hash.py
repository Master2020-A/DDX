from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
password = "admin123"
hash_password = pwd_context.hash(password)

print("Password:", password)
print("Hash:", hash_password)
