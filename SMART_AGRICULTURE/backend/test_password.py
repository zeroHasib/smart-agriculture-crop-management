
from password_utils import hash_password, verify_password

password = "Farmer@123"

# Generate password hash
stored_hash = hash_password(password)

print("Stored password hash:")
print(stored_hash)

# Test correct password
print("\nCorrect password:",
      verify_password("Farmer@123", stored_hash))

# Test incorrect password
print("Wrong password:",
      verify_password("WrongPassword", stored_hash))


from database import get_connection
from password_utils import verify_password
from getpass import getpass

email = input("Enter your email: ")
password = getpass("Enter your password: ")

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    "SELECT password_hash FROM farmers WHERE email = %s",
    (email,)
)

result = cursor.fetchone()

if result:
    stored_hash = result[0]

    if verify_password(password, stored_hash):
        print("Password verification successful!")
    else:
        print("Password verification failed!")
else:
    print("Farmer not found!")

cursor.close()
connection.close()