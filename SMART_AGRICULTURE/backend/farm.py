
from database import get_connection
from session import require_login


# ==========================================
# HELPER: GET LOGGED-IN FARMER
# ==========================================

def get_logged_in_farmer():
    session = require_login()

    if session is None:
        return None

    return session["farmer_id"]


# ==========================================
# 1. ADD FARM
# ==========================================

def add_farm(farm_name, district):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return None

    if not farm_name.strip() or not district.strip():
        print("Farm name and district are required.")
        return None

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO farms (farmer_id, farm_name, district)
            VALUES (%s, %s, %s)
        """

        values = (farmer_id, farm_name.strip(), district.strip())

        cursor.execute(query, values)
        connection.commit()

        farm_id = cursor.lastrowid

        print("Farm added successfully!")
        print("Farm ID:", farm_id)

        return farm_id

    except Exception as error:
        connection.rollback()
        print("Farm creation failed:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 2. VIEW MY FARMS
# ==========================================

def view_my_farms():

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            SELECT farm_id, farm_name, district
            FROM farms
            WHERE farmer_id = %s
            ORDER BY farm_id
        """

        cursor.execute(query, (farmer_id,))
        farms = cursor.fetchall()

        print("\n========== MY FARMS ==========")

        if not farms:
            print("You have not added any farms yet.")
            return

        for farm in farms:
            print("------------------------------")
            print("Farm ID:", farm[0])
            print("Farm Name:", farm[1])
            print("District:", farm[2])

    except Exception as error:
        print("Error viewing farms:", error)

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 3. UPDATE MY FARM
# ==========================================

def update_farm(farm_id, farm_name, district):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            UPDATE farms
            SET farm_name = %s, district = %s
            WHERE farm_id = %s AND farmer_id = %s
        """

        values = (
            farm_name.strip(),
            district.strip(),
            farm_id,
            farmer_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount > 0:
            print("Farm updated successfully!")
            return True

        print("Farm not found or access denied.")
        return False

    except Exception as error:
        connection.rollback()
        print("Farm update failed:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 4. DELETE MY FARM
# ==========================================

def delete_farm(farm_id):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            DELETE FROM farms
            WHERE farm_id = %s AND farmer_id = %s
        """

        cursor.execute(query, (farm_id, farmer_id))
        connection.commit()

        if cursor.rowcount > 0:
            print("Farm deleted successfully!")
            return True

        print("Farm not found or access denied.")
        return False

    except Exception as error:
        connection.rollback()
        print("Farm deletion failed:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 5. ADD FIELD
# ==========================================

def add_field(farm_id, field_name, area_acres,
              soil_type, soil_ph):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return None

    if not field_name.strip():
        print("Field name is required.")
        return None

    if area_acres <= 0:
        print("Field area must be greater than zero.")
        return None

    if soil_ph is not None and not 0 <= soil_ph <= 14:
        print("Soil pH must be between 0 and 14.")
        return None

    connection = get_connection()

    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Check farm ownership first
        cursor.execute(
            """
            SELECT farm_id
            FROM farms
            WHERE farm_id = %s AND farmer_id = %s
            """,
            (farm_id, farmer_id)
        )

        if cursor.fetchone() is None:
            print("Access denied! This is not your farm.")
            return None

        query = """
            INSERT INTO fields
            (farm_id, field_name, area_acres, soil_type, soil_ph)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            farm_id,
            field_name.strip(),
            area_acres,
            soil_type,
            soil_ph
        )

        cursor.execute(query, values)
        connection.commit()

        field_id = cursor.lastrowid

        print("Field added successfully!")
        print("Field ID:", field_id)

        return field_id

    except Exception as error:
        connection.rollback()
        print("Field creation failed:", error)
        return None

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 6. VIEW MY FIELDS
# ==========================================

def view_my_fields():

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            SELECT
                fields.field_id,
                fields.field_name,
                fields.area_acres,
                fields.soil_type,
                fields.soil_ph,
                farms.farm_name
            FROM fields
            INNER JOIN farms
                ON fields.farm_id = farms.farm_id
            WHERE farms.farmer_id = %s
            ORDER BY fields.field_id
        """

        cursor.execute(query, (farmer_id,))
        fields = cursor.fetchall()

        print("\n========== MY FIELDS ==========")

        if not fields:
            print("You have not added any fields yet.")
            return

        for field in fields:
            print("------------------------------")
            print("Field ID:", field[0])
            print("Field Name:", field[1])
            print("Area:", field[2], "acres")
            print("Soil Type:", field[3])
            print("Soil pH:", field[4])
            print("Farm Name:", field[5])

    except Exception as error:
        print("Error viewing fields:", error)

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 7. UPDATE MY FIELD
# ==========================================

def update_field(field_id, field_name, area_acres,
                 soil_type, soil_ph):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return False

    if not field_name.strip() or area_acres <= 0:
        print("Invalid field information.")
        return False

    if soil_ph is not None and not 0 <= soil_ph <= 14:
        print("Soil pH must be between 0 and 14.")
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            UPDATE fields
            INNER JOIN farms
                ON fields.farm_id = farms.farm_id
            SET
                fields.field_name = %s,
                fields.area_acres = %s,
                fields.soil_type = %s,
                fields.soil_ph = %s
            WHERE
                fields.field_id = %s
                AND farms.farmer_id = %s
        """

        values = (
            field_name.strip(),
            area_acres,
            soil_type,
            soil_ph,
            field_id,
            farmer_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount > 0:
            print("Field updated successfully!")
            return True

        print("Field not found or access denied.")
        return False

    except Exception as error:
        connection.rollback()
        print("Field update failed:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# ==========================================
# 8. DELETE MY FIELD
# ==========================================

def delete_field(field_id):

    farmer_id = get_logged_in_farmer()

    if farmer_id is None:
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            DELETE fields
            FROM fields
            INNER JOIN farms
                ON fields.farm_id = farms.farm_id
            WHERE
                fields.field_id = %s
                AND farms.farmer_id = %s
        """

        cursor.execute(query, (field_id, farmer_id))
        connection.commit()

        if cursor.rowcount > 0:
            print("Field deleted successfully!")
            return True

        print("Field not found or access denied.")
        return False

    except Exception as error:
        connection.rollback()
        print("Field deletion failed:", error)
        return False

    finally:
        cursor.close()
        connection.close()
