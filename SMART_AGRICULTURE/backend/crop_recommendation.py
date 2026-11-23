
from database import get_connection


def recommend_crops(district, upazila, season):

    connection = get_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = None

    query = """
        SELECT
            c.crop_name,
            cs.crop_variety,
            cs.crop_characteristic,
            cs.very_suitable_area,
            cs.suitable_area,
            cs.moderately_suitable_area,
            cs.marginally_suitable_area,
            cs.not_suitable_area

        FROM crop_suitability_data cs

        JOIN crops c
            ON cs.crop_id = c.crop_id

        WHERE LOWER(cs.district) = LOWER(%s)
          AND LOWER(cs.upazila) = LOWER(%s)
          AND cs.season = %s

          AND (
              COALESCE(cs.very_suitable_area, 0) > 0
              OR COALESCE(cs.suitable_area, 0) > 0
              OR COALESCE(cs.moderately_suitable_area, 0) > 0
              OR COALESCE(cs.marginally_suitable_area, 0) > 0
          )

        ORDER BY
            COALESCE(cs.very_suitable_area, 0) DESC
    """

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            query,
            (district.strip(), upazila.strip(), season)
        )

        results = cursor.fetchall()

        print("\n====================================")
        print("       CROP RECOMMENDATION REPORT")
        print("====================================")

        print("District:", district)
        print("Upazila:", upazila)
        print("Season:", season)

        if not results:
            print("\nNo suitable crop data found!")
            return

        for index, crop in enumerate(results, start=1):

            print("\n------------------------------------")
            print("Recommendation:", index)

            print("Crop:", crop["crop_name"])
            print("Variety:", crop["crop_variety"])

            print(
                "Characteristic:",
                crop["crop_characteristic"] or "Not specified"
            )

            print(
                "Very Suitable Area:",
                crop["very_suitable_area"]
            )

            print(
                "Suitable Area:",
                crop["suitable_area"]
            )

            print(
                "Moderately Suitable Area:",
                crop["moderately_suitable_area"]
            )

            print(
                "Marginally Suitable Area:",
                crop["marginally_suitable_area"]
            )

            print(
                "Not Suitable Area:",
                crop["not_suitable_area"]
            )

        print("\n====================================")
        print("Recommendation report completed!")
        print("====================================")

        print(
            "\nNote: Recommendations are based on "
            "upazila-level BARC suitability data."
        )

        print(
            "They are not guaranteed predictions "
            "for individual fields."
        )

    except Exception as error:

        print("\nError generating recommendations:", error)

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()
