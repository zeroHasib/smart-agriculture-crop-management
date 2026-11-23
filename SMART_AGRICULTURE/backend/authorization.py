
from database import get_connection
from session import require_login


# Check whether the logged-in farmer owns a farm
def farmer_owns_farm(farm_id):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            SELECT farm_id
            FROM farms
            WHERE farm_id = %s
            AND farmer_id = %s
        """

        cursor.execute(query, (farm_id, farmer_id))

        result = cursor.fetchone()

        return result is not None

    except Exception as error:
        print("Authorization error:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# Check whether the logged-in farmer owns a field
def farmer_owns_field(field_id):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
            SELECT fields.field_id
            FROM fields
            INNER JOIN farms
            ON fields.farm_id = farms.farm_id
            WHERE fields.field_id = %s
            AND farms.farmer_id = %s
        """

        cursor.execute(query, (field_id, farmer_id))

        result = cursor.fetchone()

        return result is not None

    except Exception as error:
        print("Authorization error:", error)
        return False

    finally:
        cursor.close()
        connection.close()
