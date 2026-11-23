
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from farm import view_my_fields, delete_field


def main():
    print("===== FIELD DELETE TEST =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:
        print("\n--- Your Fields ---")
        view_my_fields()

        field_id = int(input("\nEnter Field ID to delete: "))

        confirm = input(
            "Are you sure you want to delete this field? (yes/no): "
        )

        if confirm.lower() == "yes":
            delete_field(field_id)
        else:
            print("Delete cancelled.")

        print("\n--- Fields After Delete ---")
        view_my_fields()

    except ValueError:
        print("Invalid Field ID. Please enter a number.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
