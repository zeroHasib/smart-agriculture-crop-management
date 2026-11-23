
from database import get_connection
from session import require_login


def view_profit_loss():

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
                c.crop_name,

                COALESCE(h.total_harvested, 0),
                COALESCE(h.total_sold, 0),
                COALESCE(h.total_revenue, 0),

                COALESCE(e.total_expenses, 0),
                COALESCE(a.total_activity_cost, 0)

            FROM planting_cycles pc

            INNER JOIN fields f
                ON pc.field_id = f.field_id

            INNER JOIN farms farm
                ON f.farm_id = farm.farm_id

            INNER JOIN crops c
                ON pc.crop_id = c.crop_id

            LEFT JOIN (
                SELECT
                    cycle_id,
                    SUM(harvested_quantity_kg) AS total_harvested,
                    SUM(sold_quantity_kg) AS total_sold,
                    SUM(sold_quantity_kg * price_per_kg) AS total_revenue
                FROM harvests
                GROUP BY cycle_id
            ) h ON pc.cycle_id = h.cycle_id

            LEFT JOIN (
                SELECT
                    cycle_id,
                    SUM(amount) AS total_expenses
                FROM expenses
                GROUP BY cycle_id
            ) e ON pc.cycle_id = e.cycle_id

            LEFT JOIN (
                SELECT
                    cycle_id,
                    SUM(cost) AS total_activity_cost
                FROM farming_activities
                GROUP BY cycle_id
            ) a ON pc.cycle_id = a.cycle_id

            WHERE farm.farmer_id = %s

            ORDER BY pc.cycle_id DESC
        """

        cursor.execute(query, (farmer_id,))
        results = cursor.fetchall()

        print("\n========== FARM PROFIT / LOSS REPORT ==========")

        if not results:
            print("No planting cycle found.")
            return

        for result in results:

            (
                cycle_id,
                crop_name,
                total_harvested,
                total_sold,
                total_revenue,
                total_expenses,
                total_activity_cost
            ) = result

            total_cost = total_expenses + total_activity_cost

            profit_loss = total_revenue - total_cost

            print("\n---------------------------------------")
            print("Cycle ID:", cycle_id)
            print("Crop:", crop_name)

            print("Total Harvested:", total_harvested, "kg")
            print("Total Sold:", total_sold, "kg")

            print("Total Revenue: Tk.", f"{total_revenue:.2f}")
            print("Other Expenses: Tk.", f"{total_expenses:.2f}")
            print("Activity Costs: Tk.", f"{total_activity_cost:.2f}")

            print("Total Cost: Tk.", f"{total_cost:.2f}")

            if profit_loss > 0:
                print("Net Profit: Tk.", f"{profit_loss:.2f}")
            elif profit_loss < 0:
                print("Net Loss: Tk.", f"{abs(profit_loss):.2f}")
            else:
                print("Break-even: No profit, no loss.")

        print("\n=======================================")

    except Exception as error:
        print("Error calculating profit/loss:", error)

    finally:
        cursor.close()
        connection.close()
