
from database import get_connection
from session import require_login


# 1. Add Expense
def add_expense(cycle_id, expense_type, expense_date, description, amount):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    if not expense_type.strip():
        print("Expense type is required.")
        return False

    if amount < 0:
        print("Expense amount cannot be negative.")
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Check whether the planting cycle belongs to this farmer
        check_query = """
            SELECT pc.cycle_id
            FROM planting_cycles pc
            INNER JOIN fields f
                ON pc.field_id = f.field_id
            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id
            WHERE pc.cycle_id = %s
              AND farm.farmer_id = %s
        """

        cursor.execute(check_query, (cycle_id, farmer_id))
        result = cursor.fetchone()

        if result is None:
            print("Cycle not found or access denied.")
            return False

        # Insert expense into database
        insert_query = """
            INSERT INTO expenses
            (cycle_id, expense_type, expense_date, description, amount)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            cycle_id,
            expense_type.strip(),
            expense_date,
            description,
            amount
        )

        cursor.execute(insert_query, values)
        connection.commit()

        print("Expense added successfully!")
        print("Expense ID:", cursor.lastrowid)

        return True

    except Exception as error:
        connection.rollback()
        print("Error adding expense:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# 2. View My Expenses
def view_expenses():

    session = require_login()

    if session is None:
        return

    farmer_id = session["farmer_id"]

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            SELECT
                e.expense_id,
                c.crop_name,
                e.expense_type,
                e.expense_date,
                e.description,
                e.amount

            FROM expenses e

            INNER JOIN planting_cycles pc
                ON e.cycle_id = pc.cycle_id

            INNER JOIN fields f
                ON pc.field_id = f.field_id

            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id

            INNER JOIN crops c
                ON pc.crop_id = c.crop_id

            WHERE farm.farmer_id = %s

            ORDER BY e.expense_id DESC
        """

        cursor.execute(query, (farmer_id,))
        expenses = cursor.fetchall()

        print("\n========== MY EXPENSES ==========")

        if not expenses:
            print("No expenses found.")
            return

        total_expense = 0

        for expense in expenses:

            expense_id, crop_name, expense_type, expense_date, description, amount = expense

            print("---------------------------------------")
            print("Expense ID:", expense_id)
            print("Crop:", crop_name)
            print("Expense Type:", expense_type)
            print("Date:", expense_date)
            print("Description:", description)
            print("Amount:", amount)

            total_expense += amount

        print("---------------------------------------")
        print("Total Expense:", total_expense)

    except Exception as error:
        print("Error viewing expenses:", error)

    finally:
        cursor.close()
        connection.close()
