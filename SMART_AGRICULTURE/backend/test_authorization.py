
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from authorization import farmer_owns_farm, farmer_owns_field


print("===== FARMER AUTHORIZATION TEST =====")

email = input("Enter your email: ")
password = getpass("Enter your password: ")

farmer_id = login_farmer(email, password)

if farmer_id:

    start_session(farmer_id, email)

    print("\n--- Farm Ownership Test ---")

    farm_id = int(input("Enter Farm ID to access: "))

    if farmer_owns_farm(farm_id):
        print("Access granted! This is your farm.")
    else:
        print("Access denied! You do not own this farm.")

    print("\n--- Field Ownership Test ---")

    field_id = int(input("Enter Field ID to access: "))

    if farmer_owns_field(field_id):
        print("Access granted! This is your field.")
    else:
        print("Access denied! You do not own this field.")

    end_session()

else:
    print("Login required. Authorization test stopped.")
