
from database import get_connection
from session import require_login


# ==========================================
# 1. ADD PLANTING CYCLE
# ==========================================

def add_planting_cycle(field_id, crop_id, planting_date, expected_harvest_date):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Check field ownership and crop existence
        check_query = """
            SELECT fields.field_id
            FROM fields
            INNER JOIN farms
                ON fields.farm_id = farms.farm_id
            INNER JOIN crops
                ON crops.crop_id = %s
            WHERE fields.field_id = %s
              AND farms.farmer_id = %s
              AND crops.is_active = TRUE
        """

        cursor.execute(
            check_query,
            (crop_id, field_id, farmer_id)
        )

        result = cursor.fetchone()

        if result is None:
            print("Invalid field or crop, or access denied.")
            return False

        # Insert planting cycle
        insert_query = """
            INSERT INTO planting_cycles
            (field_id, crop_id, planting_date, expected_harvest_date)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            field_id,
            crop_id,
            planting_date,
            expected_harvest_date
        )

        cursor.execute(insert_query, values)
        connection.commit()

        print("Planting cycle added successfully!")
        print("Cycle ID:", cursor.lastrowid)

        return True

    except Exception as error:
        connection.rollback()
        print("Error adding planting cycle:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 2. VIEW MY PLANTING CYCLES
# ==========================================

def view_planting_cycles():

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
                pc.cycle_id,
                f.field_name,
                c.crop_name,
                pc.planting_date,
                pc.expected_harvest_date,
                pc.status
            FROM planting_cycles pc
            INNER JOIN fields f
                ON pc.field_id = f.field_id
            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id
            INNER JOIN crops c
                ON pc.crop_id = c.crop_id
            WHERE farm.farmer_id = %s
            ORDER BY pc.cycle_id DESC
        """

        cursor.execute(query, (farmer_id,))
        cycles = cursor.fetchall()

        print("\n========== MY PLANTING CYCLES ==========")

        if not cycles:
            print("No planting cycles found.")
            return

        for cycle in cycles:

            cycle_id, field_name, crop_name, planting_date, harvest_date, status = cycle

            print("---------------------------------------")
            print("Cycle ID:", cycle_id)
            print("Field Name:", field_name)
            print("Crop Name:", crop_name)
            print("Planting Date:", planting_date)
            print("Expected Harvest:", harvest_date)
            print("Status:", status)

        print("---------------------------------------")

    except Exception as error:
        print("Error viewing planting cycles:", error)

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 3. UPDATE PLANTING STATUS
# ==========================================

def update_planting_status(cycle_id, new_status):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    allowed_statuses = [
        "Growing",
        "Harvested",
        "Failed"
    ]

    if new_status not in allowed_statuses:
        print("Invalid status!")
        print("Allowed: Growing, Harvested, Failed")
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            UPDATE planting_cycles pc
            INNER JOIN fields f
                ON pc.field_id = f.field_id
            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id
            SET pc.status = %s
            WHERE pc.cycle_id = %s
              AND farm.farmer_id = %s
        """

        cursor.execute(
            query,
            (new_status, cycle_id, farmer_id)
        )

        connection.commit()

        if cursor.rowcount > 0:
            print("Planting status updated successfully!")
            return True

        print("Cycle not found or access denied.")
        return False

    except Exception as error:
        connection.rollback()
        print("Error updating planting status:", error)
        return False

    finally:
        cursor.close()
        connection.close()
