
from database import get_connection
from session import require_login


# 1. Add Harvest
def add_harvest(cycle_id, harvest_date, harvested_quantity,
                sold_quantity, price_per_kg, description):

    session = require_login()

    if session is None:
        return False

    farmer_id = session["farmer_id"]

    # Validate input
    if harvested_quantity <= 0:
        print("Harvested quantity must be greater than zero.")
        return False

    if sold_quantity < 0 or sold_quantity > harvested_quantity:
        print("Invalid sold quantity.")
        return False

    if price_per_kg < 0:
        print("Price cannot be negative.")
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Check planting cycle ownership
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

        # Insert harvest record
        insert_query = """
            INSERT INTO harvests
            (
                cycle_id,
                harvest_date,
                harvested_quantity_kg,
                sold_quantity_kg,
                price_per_kg,
                description
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            cycle_id,
            harvest_date,
            harvested_quantity,
            sold_quantity,
            price_per_kg,
            description
        )

        cursor.execute(insert_query, values)
        connection.commit()

        print("Harvest record added successfully!")
        print("Harvest ID:", cursor.lastrowid)

        return True

    except Exception as error:
        connection.rollback()
        print("Error adding harvest:", error)
        return False

    finally:
        cursor.close()
        connection.close()


# 2. View Harvest Records
def view_harvests():

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
                h.harvest_id,
                c.crop_name,
                h.harvest_date,
                h.harvested_quantity_kg,
                h.sold_quantity_kg,
                h.price_per_kg,
                h.description

            FROM harvests h

            INNER JOIN planting_cycles pc
                ON h.cycle_id = pc.cycle_id

            INNER JOIN fields f
                ON pc.field_id = f.field_id

            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id

            INNER JOIN crops c
                ON pc.crop_id = c.crop_id

            WHERE farm.farmer_id = %s

            ORDER BY h.harvest_id DESC
        """

        cursor.execute(query, (farmer_id,))
        harvests = cursor.fetchall()

        print("\n========== MY HARVEST RECORDS ==========")

        if not harvests:
            print("No harvest records found.")
            return

        total_harvested = 0
        total_sold = 0
        total_revenue = 0

        for harvest in harvests:

            (harvest_id, crop_name, harvest_date,
             harvested_quantity, sold_quantity,
             price_per_kg, description) = harvest

            remaining = harvested_quantity - sold_quantity
            revenue = sold_quantity * price_per_kg

            print("---------------------------------------")
            print("Harvest ID:", harvest_id)
            print("Crop:", crop_name)
            print("Harvest Date:", harvest_date)
            print("Harvested Quantity:", harvested_quantity, "kg")
            print("Sold Quantity:", sold_quantity, "kg")
            print("Remaining Quantity:", remaining, "kg")
            print("Price per KG:", price_per_kg)
            print("Revenue:", revenue)
            print("Description:", description)

            total_harvested += harvested_quantity
            total_sold += sold_quantity
            total_revenue += revenue

        print("---------------------------------------")
        print("Total Harvested:", total_harvested, "kg")
        print("Total Sold:", total_sold, "kg")
        print("Total Remaining:", total_harvested - total_sold, "kg")
        print("Total Revenue:", total_revenue)

    except Exception as error:
        print("Error viewing harvests:", error)

    finally:
        cursor.close()
        connection.close()
