
from database import get_connection
from session import require_login


# 1. Add Farming Activity
def add_activity(cycle_id, activity_type, activity_date, description, cost):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    if not activity_type.strip():
        print("Activity type is required.")
        return False

    if cost < 0:
        print("Cost cannot be negative.")
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Check whether this planting cycle belongs to the logged-in farmer
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

        # Insert farming activity
        insert_query = """
            INSERT INTO farming_activities
            (cycle_id, activity_type, activity_date, description, cost)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            cycle_id,
            activity_type.strip(),
            activity_date,
            description,
            cost
        )

        cursor.execute(insert_query, values)
        connection.commit()

        print("Farming activity added successfully!")
        print("Activity ID:", cursor.lastrowid)

        return True

    except Exception as error:
        connection.rollback()
        print("Error adding activity:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# 2. View Farming Activities
def view_activities():

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
                a.activity_id,
                c.crop_name,
                a.activity_type,
                a.activity_date,
                a.description,
                a.cost

            FROM farming_activities a

            INNER JOIN planting_cycles pc
                ON a.cycle_id = pc.cycle_id

            INNER JOIN fields f
                ON pc.field_id = f.field_id

            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id

            INNER JOIN crops c
                ON pc.crop_id = c.crop_id

            WHERE farm.farmer_id = %s

            ORDER BY a.activity_id DESC
        """

        cursor.execute(query, (farmer_id,))
        activities = cursor.fetchall()

        print("\n========== MY FARMING ACTIVITIES ==========")

        if not activities:
            print("No farming activities found.")
            return

        for activity in activities:

            activity_id, crop_name, activity_type, activity_date, description, cost = activity

            print("---------------------------------------")
            print("Activity ID:", activity_id)
            print("Crop:", crop_name)
            print("Activity:", activity_type)
            print("Date:", activity_date)
            print("Description:", description)
            print("Cost:", cost)

        print("---------------------------------------")

    except Exception as error:
        print("Error viewing activities:", error)

    finally:
        cursor.close()
        connection.close()
