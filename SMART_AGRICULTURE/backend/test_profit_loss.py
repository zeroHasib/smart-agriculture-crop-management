
from getpass import getpass

from farmer import login_farmer
from session import start_session, end_session
from profit_loss import view_profit_loss


def main():

    print("===== PROFIT / LOSS MANAGEMENT =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- My Profit / Loss Report ---")

        view_profit_loss()

    finally:
        end_session()


if __name__ == "__main__":
    main()
