
from getpass import getpass
from datetime import date

from farmer import login_farmer
from session import start_session, end_session
from expense import add_expense, view_expenses


def main():

    print("===== EXPENSE MANAGEMENT =====")

    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    farmer_id = login_farmer(email, password)

    if farmer_id is None:
        print("Login failed!")
        return

    start_session(farmer_id, email)

    try:

        print("\n--- Add New Expense ---")

        cycle_id = int(input("Enter Cycle ID: "))

        print("\n1. Seeds")
        print("2. Fertilizer")
        print("3. Labour")
        print("4. Irrigation")
        print("5. Pesticide")
        print("6. Other")

        choice = input("Choose expense type: ")

        expense_options = {
            "1": "Seeds",
            "2": "Fertilizer",
            "3": "Labour",
            "4": "Irrigation",
            "5": "Pesticide",
            "6": "Other"
        }

        expense_type = expense_options.get(choice)

        if expense_type is None:
            print("Invalid expense choice!")
            return

        expense_date = input("Enter expense date (YYYY-MM-DD): ")

        date.fromisoformat(expense_date)

        description = input("Enter description: ")

        amount = float(input("Enter expense amount: "))

        if amount < 0:
            print("Amount cannot be negative.")
            return

        add_expense(
            cycle_id,
            expense_type,
            expense_date,
            description,
            amount
        )

        print("\n--- View My Expenses ---")

        view_expenses()

    except ValueError:
        print("Invalid input! Check Cycle ID, date and amount.")

    finally:
        end_session()


if __name__ == "__main__":
    main()
