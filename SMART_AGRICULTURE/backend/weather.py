
import json

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

from database import get_connection


# ==========================================
# 1. WEATHER CONDITION DESCRIPTION
# ==========================================

def get_weather_description(code):

    weather_codes = {

        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing Rime Fog",

        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",

        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",

        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",

        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",

        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Heavy Thunderstorm with Hail"

    }

    return weather_codes.get(code, "Unknown Weather")


# ==========================================
# 2. WEATHER-BASED FARMING ADVISORY
# ==========================================

def generate_farming_advisory(daily):

    print("\n================================")
    print("       FARMING ADVISORY")
    print("================================")

    advisory_found = False

    for i in range(len(daily["time"])):

        date = daily["time"][i]

        rain_probability = daily["precipitation_probability_max"][i]

        rainfall = daily["precipitation_sum"][i]

        wind_speed = daily["wind_speed_10m_max"][i]

        max_temperature = daily["temperature_2m_max"][i]

        print("\nDate:", date)

        # Rain probability warning

        if (
            rain_probability is not None
            and rain_probability >= 60
        ):

            print("\nRAIN WARNING:")

            print(
                "Check rainfall conditions before "
                "scheduling irrigation."
            )

            advisory_found = True

        # Heavy rainfall warning

        if (
            rainfall is not None
            and rainfall >= 20
        ):

            print("\nHEAVY RAIN WARNING:")

            print(
                "Inspect field drainage and take precautions "
                "against waterlogging."
            )

            advisory_found = True

        # Strong wind warning

        if (
            wind_speed is not None
            and wind_speed >= 30
        ):

            print("\nWIND WARNING:")

            print(
                "Check crop supports and protect "
                "vulnerable plants."
            )

            advisory_found = True

        # High temperature warning

        if (
            max_temperature is not None
            and max_temperature >= 35
        ):

            print("\nHIGH TEMPERATURE WARNING:")

            print(
                "Monitor soil moisture and check "
                "crops for heat stress."
            )

            advisory_found = True

    if not advisory_found:

        print("\nNo special weather warnings detected.")

        print(
            "Continue regular crop monitoring "
            "and follow normal farming practices."
        )

    print("\n================================")
    print("Farming advisory completed!")
    print("================================")


# ==========================================
# 3. MAIN WEATHER FUNCTION
# ==========================================

def view_weather_forecast(farmer_id):

    connection = get_connection()

    if connection is None:

        print("Database connection failed!")
        return

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        query = """

            SELECT
                farm_id,
                farm_name,
                district,
                latitude,
                longitude

            FROM farms

            WHERE farmer_id = %s

            ORDER BY farm_id

        """

        cursor.execute(query, (farmer_id,))

        farms = cursor.fetchall()

    except Exception as error:

        print("Error loading farms:", error)
        return

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()

    # Check available farms

    if not farms:

        print("No farms found for this farmer!")
        return

    # ======================================
    # 4. FARM SELECTION
    # ======================================

    print("\n================================")
    print("       SELECT YOUR FARM")
    print("================================")

    available_farms = []

    for farm in farms:

        if (
            farm["latitude"] is None
            or farm["longitude"] is None
        ):

            continue

        available_farms.append(farm)

        print(
            len(available_farms),
            ".",
            farm["farm_name"],
            "-",
            farm["district"]
        )

    if not available_farms:

        print("No farm has valid coordinates!")
        return

    try:

        choice = int(input("\nSelect farm number: "))

        if choice < 1 or choice > len(available_farms):

            print("Invalid farm selection!")
            return

    except ValueError:

        print("Please enter a valid number!")
        return

    selected_farm = available_farms[choice - 1]

    latitude = float(selected_farm["latitude"])

    longitude = float(selected_farm["longitude"])

    # ======================================
    # 5. WEATHER INFORMATION
    # ======================================

    print("\n================================")
    print("       WEATHER INFORMATION")
    print("================================")

    print("Farm:", selected_farm["farm_name"])

    print("District:", selected_farm["district"])

    print("Latitude:", latitude)

    print("Longitude:", longitude)

    # ======================================
    # 6. OPEN-METEO API PARAMETERS
    # ======================================

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "rain,"
            "wind_speed_10m,"
            "weather_code"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),

        "forecast_days": 7,

        "timezone": "auto"

    }

    api_url = (

        "https://api.open-meteo.com/v1/forecast?"

        + urlencode(params)

    )

    try:

        # ==================================
        # 7. FETCH WEATHER DATA
        # ==================================

        with urlopen(api_url, timeout=20) as response:

            weather_data = json.loads(
                response.read().decode("utf-8")
            )

        # ==================================
        # 8. CURRENT WEATHER
        # ==================================

        current = weather_data["current"]

        print("\n========== CURRENT WEATHER ==========")

        print(
            "Condition:",
            get_weather_description(
                current["weather_code"]
            )
        )

        print(
            "Temperature:",
            current["temperature_2m"],
            "°C"
        )

        print(
            "Feels Like:",
            current["apparent_temperature"],
            "°C"
        )

        print(
            "Humidity:",
            current["relative_humidity_2m"],
            "%"
        )

        print(
            "Precipitation:",
            current["precipitation"],
            "mm"
        )

        print(
            "Rain:",
            current["rain"],
            "mm"
        )

        print(
            "Wind Speed:",
            current["wind_speed_10m"],
            "km/h"
        )

        # ==================================
        # 9. SEVEN-DAY FORECAST
        # ==================================

        daily = weather_data["daily"]

        print("\n========== 7-DAY FORECAST ==========")

        for i in range(len(daily["time"])):

            print("\n--------------------------------")

            print("Date:", daily["time"][i])

            print(
                "Condition:",
                get_weather_description(
                    daily["weather_code"][i]
                )
            )

            print(
                "Maximum Temperature:",
                daily["temperature_2m_max"][i],
                "°C"
            )

            print(
                "Minimum Temperature:",
                daily["temperature_2m_min"][i],
                "°C"
            )

            print(
                "Rain Probability:",
                daily["precipitation_probability_max"][i],
                "%"
            )

            print(
                "Expected Rainfall:",
                daily["precipitation_sum"][i],
                "mm"
            )

            print(
                "Maximum Wind Speed:",
                daily["wind_speed_10m_max"][i],
                "km/h"
            )

        # ==================================
        # 10. FARMING ADVISORY
        # ==================================

        generate_farming_advisory(daily)

        # ==================================
        # 11. COMPLETION MESSAGE
        # ==================================

        print("\n================================")

        print("Weather report completed!")

        print("================================")

        print(
            "\nNote: Weather information is based on "
            "the selected farm's saved coordinates."
        )

        print(
            "Coordinates are approximate, so the forecast "
            "may not represent the exact field."
        )

        print(
            "Farming advisories are preliminary "
            "weather-based rules, not guaranteed predictions."
        )

    except HTTPError as error:

        print("Weather API HTTP error:", error.code)

    except URLError as error:

        print("Internet connection error:", error.reason)

    except (KeyError, ValueError, TypeError) as error:

        print("Invalid weather API response:", error)

    except Exception as error:

        print("Weather error:", error)
