
from database import get_connection


# 1. ADD CROP (ADMIN FUNCTION)
def add_crop(crop_name, category, description, duration):

    if not crop_name.strip():
        print("Crop name is required.")
        return

    if duration <= 0:
        print("Growing duration must be greater than zero.")
        return

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO crops
            (crop_name, category, description, growing_duration_days)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            crop_name.strip(),
            category,
            description,
            duration
        )

        cursor.execute(query, values)
        connection.commit()

        print("Crop added successfully!")
        print("Crop ID:", cursor.lastrowid)

    except Exception as error:
        connection.rollback()

        if getattr(error, "errno", None) == 1062:
            print("This crop already exists.")
        else:
            print("Error adding crop:", error)

    finally:
        cursor.close()
        connection.close()


# 2. VIEW AVAILABLE CROPS (FARMER FUNCTION)
def view_crops():

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            SELECT crop_id, crop_name, category,
                   description, growing_duration_days
            FROM crops
            WHERE is_active = TRUE
            ORDER BY crop_id
        """

        cursor.execute(query)
        crops = cursor.fetchall()

        print("\n========== AVAILABLE CROPS ==========")

        if not crops:
            print("No available crops.")
            return

        for crop in crops:
            print("--------------------------------")
            print("Crop ID:", crop[0])
            print("Crop Name:", crop[1])
            print("Category:", crop[2])
            print("Description:", crop[3])
            print("Duration:", crop[4], "days")

    except Exception as error:
        print("Error viewing crops:", error)

    finally:
        cursor.close()
        connection.close()


# 3. UPDATE CROP (ADMIN FUNCTION)
def update_crop(crop_id, new_category, new_duration):

    if new_duration <= 0:
        print("Invalid growing duration.")
        return

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            UPDATE crops
            SET category = %s,
                growing_duration_days = %s
            WHERE crop_id = %s
        """

        values = (new_category, new_duration, crop_id)

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount > 0:
            print("Crop updated successfully!")
        else:
            print("Crop not found or information unchanged.")

    except Exception as error:
        connection.rollback()
        print("Error updating crop:", error)

    finally:
        cursor.close()
        connection.close()


# 4. DEACTIVATE CROP (ADMIN FUNCTION)
def deactivate_crop(crop_id):

    connection = get_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        query = """
            UPDATE crops
            SET is_active = FALSE
            WHERE crop_id = %s
        """

        cursor.execute(query, (crop_id,))
        connection.commit()

        if cursor.rowcount > 0:
            print("Crop deactivated successfully!")
        else:
            print("Crop not found or already inactive.")

    except Exception as error:
        connection.rollback()
        print("Error deactivating crop:", error)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":

    view_crops()
