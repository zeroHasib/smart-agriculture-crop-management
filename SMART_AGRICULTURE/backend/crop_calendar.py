
from database import get_connection


def view_crop_calendar(farmer_id):

    connection = get_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                pc.cycle_id,
                c.crop_name,
                f.field_name,
                fa.farm_name,
                pc.planting_date,
                pc.expected_harvest_date,
                pc.status,

                DATEDIFF(
                    pc.expected_harvest_date,
                    CURDATE()
                ) AS days_until_harvest

            FROM planting_cycles pc

            JOIN fields f
                ON pc.field_id = f.field_id

            JOIN farms fa
                ON f.farm_id = fa.farm_id

            JOIN crops c
                ON pc.crop_id = c.crop_id

            WHERE fa.farmer_id = %s

            ORDER BY pc.planting_date DESC
        """

        cursor.execute(query, (farmer_id,))
        cycles = cursor.fetchall()

        print("\n================================")
        print("        CROP CALENDAR")
        print("================================")

        if not cycles:
            print("No planting cycles found!")
            return

        for cycle in cycles:

            print("\n--------------------------------")
            print("Cycle ID:", cycle["cycle_id"])
            print("Farm:", cycle["farm_name"])
            print("Field:", cycle["field_name"])
            print("Crop:", cycle["crop_name"])

            print("Planting Date:", cycle["planting_date"])

            print(
                "Expected Harvest Date:",
                cycle["expected_harvest_date"] or "Not set"
            )

            print("Status:", cycle["status"])

            # Harvest countdown logic

            days = cycle["days_until_harvest"]
            status = cycle["status"]

            if status == "Harvested":

                print("Harvest Countdown: Already harvested")

            elif status == "Failed":

                print("Harvest Countdown: Crop failed")

            elif days is None:

                print("Harvest Countdown: Not available")

            elif days > 0:

                print("Harvest Countdown:", days, "days remaining")

            elif days == 0:

                print("Harvest Countdown: Expected harvest is today!")

            else:

                print(
                    "Harvest Countdown:",
                    abs(days),
                    "days past expected harvest date"
                )

            # Show farming activities for this cycle

            activity_query = """
                SELECT
                    activity_type,
                    activity_date,
                    description,
                    cost

                FROM farming_activities

                WHERE cycle_id = %s

                ORDER BY activity_date
            """

            cursor.execute(
                activity_query,
                (cycle["cycle_id"],)
            )

            activities = cursor.fetchall()

            print("\nFarming Activities:")

            if activities:

                for activity in activities:

                    print("Activity:", activity["activity_type"])
                    print("Date:", activity["activity_date"])
                    print("Description:", activity["description"])
                    print("Cost:", activity["cost"])
                    print("------------------------")

            else:

                print("No activities recorded.")

        print("\n================================")
        print("Crop calendar report completed!")
        print("================================")

    except Exception as error:

        print("Error generating crop calendar:", error)

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()
