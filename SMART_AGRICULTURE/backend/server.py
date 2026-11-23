import json
import secrets
import math

from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs

from farmer import register_farmer, login_farmer
from admin import login_admin
from database import get_connection


PROJECT_DIR = Path(__file__).resolve().parent.parent

HOST = "127.0.0.1"
PORT = 8000

active_sessions = {}
active_admin_sessions = {}


class SmartAgricultureHandler(SimpleHTTPRequestHandler):

    ACTIVITY_TYPES = [
        "Irrigation",
        "Fertilizing",
        "Pesticide",
        "Weeding",
        "Land Preparation"
    ]

    EXPENSE_TYPES = [
        "Seeds",
        "Fertilizer",
        "Irrigation",
        "Pesticide",
        "Labor",
        "Equipment",
        "Transportation",
        "Others"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(PROJECT_DIR),
            **kwargs
        )


    # =================================
    # SESSION FUNCTIONS
    # =================================

    def get_session_token(self):
        cookie_header = self.headers.get("Cookie")

        if not cookie_header:
            return None

        cookie = SimpleCookie()

        try:
            cookie.load(cookie_header)
        except Exception:
            return None

        if "farmer_session" in cookie:
            return cookie["farmer_session"].value

        return None

    def get_farmer_session(self):
        token = self.get_session_token()

        if token is None:
            return None

        return active_sessions.get(token)

    # =================================
    # ADMIN SESSION MANAGEMENT
    # =================================

    def get_admin_session_token(self):
        cookie_header = self.headers.get("Cookie")

        if not cookie_header:
            return None

        cookie = SimpleCookie()

        try:
            cookie.load(cookie_header)
        except Exception:
            return None

        if "admin_session" in cookie:
            return cookie["admin_session"].value

        return None

    def get_admin_session(self):
        token = self.get_admin_session_token()

        if token is None:
            return None

        return active_admin_sessions.get(token)

    def require_admin(self):
        admin = self.get_admin_session()

        if admin is None:
            self.send_json({
                "success": False,
                "message": "Admin login required."
            }, status=401)

            return None

        return admin

    # =================================
    # FARMER AUTHORIZATION
    # =================================

    def require_farmer(self):
        farmer = self.get_farmer_session()

        if farmer is None:
            self.send_json({
                "success": False,
                "message": "Please login first."
            }, status=401)

            return None

        return farmer

    

    def require_farmer(self):
        farmer = self.get_farmer_session()

        if farmer is None:
            self.send_json({
                "success": False,
                "message": "Please login first."
            }, status=401)

            return None

        return farmer

    # =================================
    # JSON RESPONSE
    # =================================

    def send_json(self, data, status=200, headers=None):
        response = json.dumps(
            data,
            ensure_ascii=False,
            default=str
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)

        self.end_headers()

        try:
            self.wfile.write(response)
        except (BrokenPipeError, ConnectionAbortedError):
            pass

    # =================================
    # READ JSON
    # =================================

    def read_json(self):
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        if content_length > 10000:
            raise ValueError("Request body is too large.")

        if content_length <= 0:
            return {}

        body = self.rfile.read(content_length)
        data = json.loads(body.decode("utf-8"))

        if not isinstance(data, dict):
            raise ValueError("JSON must be an object.")

        return data

    # =================================
    # DATABASE CONNECTION
    # =================================

    def get_db(self):
        connection = get_connection()

        if connection is None:
            raise Exception("Database connection failed.")

        return connection

    # =================================
    # VALIDATION HELPERS
    # =================================

    def validate_text(self, value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} is required.")

        return value.strip()

    def validate_positive_number(self, value, field_name):
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a number.")

        if not math.isfinite(number) or number <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return number

    def validate_soil_ph(self, value):
        try:
            soil_ph = float(value)
        except (TypeError, ValueError):
            raise ValueError("Soil pH must be a number.")

        if not math.isfinite(soil_ph) or not 0 <= soil_ph <= 14:
            raise ValueError("Soil pH must be between 0 and 14.")

        return soil_ph

    def validate_date(self, value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"{field_name} is required.")

        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            raise ValueError(
                f"{field_name} must use YYYY-MM-DD format."
            )

    # =================================
    # ACTIVITY VALIDATION
    # =================================

    def validate_activity_type(self, value):
        activity_type = self.validate_text(
            value,
            "Activity type"
        )

        if activity_type not in self.ACTIVITY_TYPES:
            raise ValueError("Invalid activity type.")

        return activity_type

    def validate_activity_cost(self, value):
        if value is None or value == "":
            return 0.0

        try:
            cost = float(value)
        except (TypeError, ValueError):
            raise ValueError("Activity cost must be a number.")

        if not math.isfinite(cost) or cost < 0:
            raise ValueError("Activity cost cannot be negative.")

        return cost

    # =================================
    # EXPENSE VALIDATION
    # =================================

    def validate_expense_type(self, value):
        expense_type = self.validate_text(
            value,
            "Expense category"
        )

        if expense_type not in self.EXPENSE_TYPES:
            raise ValueError("Invalid expense category.")

        return expense_type

    def validate_expense_amount(self, value):
        try:
            amount = float(value)
        except (TypeError, ValueError):
            raise ValueError("Expense amount must be a number.")

        if not math.isfinite(amount) or amount <= 0:
            raise ValueError(
                "Expense amount must be greater than zero."
            )

        if amount > 99999999.99:
            raise ValueError(
                "Expense amount exceeds the maximum limit."
            )

        return round(amount, 2)

    # =================================
    # DASHBOARD STATISTICS
    # =================================

    def get_dashboard_statistics(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM farms
                WHERE farmer_id = %s
                """,
                (farmer_id,)
            )
            total_farms = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                """,
                (farmer_id,)
            )
            total_fields = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT pc.crop_id)
                FROM planting_cycles pc
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                JOIN crops c ON pc.crop_id = c.crop_id
                WHERE fm.farmer_id = %s
                  AND pc.status = 'Growing'
                  AND c.is_active = 1
                """,
                (farmer_id,)
            )
            growing_crops = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                """,
                (farmer_id,)
            )
            total_expenses = cursor.fetchone()[0]

            return {
                "success": True,
                "statistics": {
                    "total_farms": int(total_farms or 0),
                    "total_fields": int(total_fields or 0),
                    "growing_crops": int(growing_crops or 0),
                    "total_expenses": float(total_expenses or 0)
                }
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # =================================
    # FARM MANAGEMENT
    # =================================

    def get_farmer_farms(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT farm_id, farm_name, district,
                       latitude, longitude
                FROM farms
                WHERE farmer_id = %s
                ORDER BY farm_id DESC
                """,
                (farmer_id,)
            )

            farms = []

            for row in cursor.fetchall():
                farms.append({
                    "farm_id": row[0],
                    "farm_name": row[1],
                    "district": row[2],
                    "latitude": row[3],
                    "longitude": row[4]
                })

            return {"success": True, "farms": farms}

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_farm(self, farmer_id, data):
        farm_name = self.validate_text(
            data.get("farm_name"), "Farm name"
        )
        district = self.validate_text(
            data.get("district"), "District"
        )

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO farms (farmer_id, farm_name, district)
                VALUES (%s, %s, %s)
                """,
                (farmer_id, farm_name, district)
            )

            farm_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Farm created successfully.",
                "farm_id": farm_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_farm(self, farmer_id, farm_id, data):
        farm_name = self.validate_text(
            data.get("farm_name"), "Farm name"
        )
        district = self.validate_text(
            data.get("district"), "District"
        )

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE farms
                SET farm_name = %s, district = %s
                WHERE farm_id = %s AND farmer_id = %s
                """,
                (farm_name, district, farm_id, farmer_id)
            )

            updated = cursor.rowcount
            connection.commit()

            if updated == 0:
                return {
                    "success": False,
                    "message": "Farm not found or no changes made."
                }

            return {
                "success": True,
                "message": "Farm updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_farm(self, farmer_id, farm_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM farms
                WHERE farm_id = %s AND farmer_id = %s
                """,
                (farm_id, farmer_id)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Farm not found."
                }

            return {
                "success": True,
                "message": "Farm deleted successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # =================================
    # FIELD MANAGEMENT
    # =================================

    def get_farmer_fields(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT f.field_id, f.farm_id, f.field_name,
                       f.area_acres, f.soil_type, f.soil_ph,
                       fm.farm_name
                FROM fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                ORDER BY f.field_id DESC
                """,
                (farmer_id,)
            )

            fields = []

            for row in cursor.fetchall():
                fields.append({
                    "field_id": row[0],
                    "farm_id": row[1],
                    "field_name": row[2],
                    "area_acres": float(row[3]) if row[3] is not None else 0,
                    "soil_type": row[4],
                    "soil_ph": float(row[5]) if row[5] is not None else None,
                    "farm_name": row[6]
                })

            return {"success": True, "fields": fields}

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_field(self, farmer_id, data):
        try:
            farm_id = int(data.get("farm_id"))
        except (TypeError, ValueError):
            raise ValueError("Please select a valid farm.")

        field_name = self.validate_text(
            data.get("field_name"), "Field name"
        )
        area_acres = self.validate_positive_number(
            data.get("area_acres"), "Field area"
        )
        soil_type = self.validate_text(
            data.get("soil_type"), "Soil type"
        )
        soil_ph = self.validate_soil_ph(data.get("soil_ph"))

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT farm_id FROM farms
                WHERE farm_id = %s AND farmer_id = %s
                """,
                (farm_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Selected farm does not belong to you."
                }

            cursor.execute(
                """
                INSERT INTO fields (
                    farm_id, field_name, area_acres,
                    soil_type, soil_ph
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (farm_id, field_name, area_acres, soil_type, soil_ph)
            )

            field_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Field created successfully.",
                "field_id": field_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_field(self, farmer_id, field_id, data):
        field_name = self.validate_text(
            data.get("field_name"), "Field name"
        )
        area_acres = self.validate_positive_number(
            data.get("area_acres"), "Field area"
        )
        soil_type = self.validate_text(
            data.get("soil_type"), "Soil type"
        )
        soil_ph = self.validate_soil_ph(data.get("soil_ph"))

        try:
            farm_id = int(data.get("farm_id"))
        except (TypeError, ValueError):
            raise ValueError("Please select a valid farm.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                SET f.farm_id = %s,
                    f.field_name = %s,
                    f.area_acres = %s,
                    f.soil_type = %s,
                    f.soil_ph = %s
                WHERE f.field_id = %s
                  AND fm.farmer_id = %s
                  AND EXISTS (
                      SELECT 1 FROM farms selected_farm
                      WHERE selected_farm.farm_id = %s
                        AND selected_farm.farmer_id = %s
                  )
                """,
                (
                    farm_id, field_name, area_acres,
                    soil_type, soil_ph, field_id,
                    farmer_id, farm_id, farmer_id
                )
            )

            updated = cursor.rowcount
            connection.commit()

            if updated == 0:
                return {
                    "success": False,
                    "message": "Field not found or no changes made."
                }

            return {
                "success": True,
                "message": "Field updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_field(self, farmer_id, field_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE f
                FROM fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE f.field_id = %s AND fm.farmer_id = %s
                """,
                (field_id, farmer_id)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Field not found."
                }

            return {
                "success": True,
                "message": "Field deleted successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # =================================
    # CROP MANAGEMENT
    # =================================

    def get_all_crops(self):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT crop_id, crop_name, category,
                       description, growing_duration_days
                FROM crops
                WHERE is_active = 1
                ORDER BY crop_name
                """
            )

            crops = []

            for row in cursor.fetchall():
                crops.append({
                    "crop_id": row[0],
                    "crop_name": row[1],
                    "category": row[2],
                    "description": row[3],
                    "growing_duration_days": row[4]
                })

            return {"success": True, "crops": crops}

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_crop(self, data):
        crop_name = self.validate_text(
            data.get("crop_name"), "Crop name"
        )
        category = self.validate_text(
            data.get("category"), "Crop category"
        )
        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid crop description.")

        try:
            duration = int(data.get("growing_duration_days"))
        except (TypeError, ValueError):
            raise ValueError("Growing duration must be a valid number.")

        if duration <= 0:
            raise ValueError("Growing duration must be greater than zero.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT crop_id FROM crops
                WHERE LOWER(crop_name) = LOWER(%s)
                """,
                (crop_name,)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "This crop already exists."
                }

            cursor.execute(
                """
                INSERT INTO crops (
                    crop_name, category, description,
                    growing_duration_days, is_active
                )
                VALUES (%s, %s, %s, %s, 1)
                """,
                (crop_name, category, description.strip(), duration)
            )

            crop_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Crop added successfully.",
                "crop_id": crop_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_crop(self, crop_id, data):
        crop_name = self.validate_text(
            data.get("crop_name"), "Crop name"
        )
        category = self.validate_text(
            data.get("category"), "Crop category"
        )
        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid crop description.")

        try:
            duration = int(data.get("growing_duration_days"))
        except (TypeError, ValueError):
            raise ValueError("Growing duration must be a valid number.")

        if duration <= 0:
            raise ValueError("Growing duration must be greater than zero.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT crop_id FROM crops
                WHERE crop_id = %s AND is_active = 1
                """,
                (crop_id,)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Crop not found or inactive."
                }

            cursor.execute(
                """
                SELECT crop_id FROM crops
                WHERE LOWER(crop_name) = LOWER(%s)
                  AND crop_id != %s
                """,
                (crop_name, crop_id)
            )

            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "Another crop with this name already exists."
                }

            cursor.execute(
                """
                UPDATE crops
                SET crop_name = %s,
                    category = %s,
                    description = %s,
                    growing_duration_days = %s
                WHERE crop_id = %s AND is_active = 1
                """,
                (crop_name, category, description.strip(), duration, crop_id)
            )

            connection.commit()

            return {
                "success": True,
                "message": "Crop updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_crop(self, crop_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE crops
                SET is_active = 0
                WHERE crop_id = %s AND is_active = 1
                """,
                (crop_id,)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Crop not found or already inactive."
                }

            return {
                "success": True,
                "message": "Crop deactivated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # =================================
    # PLANTING CYCLE MANAGEMENT
    # =================================

    def get_planting_cycles(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    pc.cycle_id,
                    pc.field_id,
                    pc.crop_id,
                    pc.planting_date,
                    pc.expected_harvest_date,
                    pc.status,
                    f.field_name,
                    fm.farm_name,
                    c.crop_name
                FROM planting_cycles pc
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                JOIN crops c ON pc.crop_id = c.crop_id
                WHERE fm.farmer_id = %s
                ORDER BY pc.cycle_id DESC
                """,
                (farmer_id,)
            )

            cycles = []

            for row in cursor.fetchall():
                cycles.append({
                    "cycle_id": row[0],
                    "field_id": row[1],
                    "crop_id": row[2],
                    "planting_date": str(row[3]) if row[3] else None,
                    "expected_harvest_date": str(row[4]) if row[4] else None,
                    "status": row[5],
                    "field_name": row[6],
                    "farm_name": row[7],
                    "crop_name": row[8]
                })

            return {
                "success": True,
                "planting_cycles": cycles
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_planting_cycle(self, farmer_id, data):
        try:
            field_id = int(data.get("field_id"))
            crop_id = int(data.get("crop_id"))

            if field_id <= 0 or crop_id <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Please select a valid field and crop.")

        planting_date = self.validate_date(
            data.get("planting_date"), "Planting date"
        )
        expected_harvest_date = self.validate_date(
            data.get("expected_harvest_date"), "Expected harvest date"
        )

        if expected_harvest_date < planting_date:
            raise ValueError(
                "Harvest date cannot be earlier than planting date."
            )

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT f.field_id
                FROM fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE f.field_id = %s AND fm.farmer_id = %s
                """,
                (field_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Selected field does not belong to you."
                }

            cursor.execute(
                """
                SELECT crop_id FROM crops
                WHERE crop_id = %s AND is_active = 1
                """,
                (crop_id,)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Selected crop is not available."
                }

            cursor.execute(
                """
                INSERT INTO planting_cycles (
                    field_id, crop_id, planting_date,
                    expected_harvest_date, status
                )
                VALUES (%s, %s, %s, %s, 'Growing')
                """,
                (field_id, crop_id, planting_date, expected_harvest_date)
            )

            cycle_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Planting cycle created successfully.",
                "cycle_id": cycle_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_planting_cycle(self, farmer_id, cycle_id, data):
        try:
            field_id = int(data.get("field_id"))
            crop_id = int(data.get("crop_id"))

            if field_id <= 0 or crop_id <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Please select a valid field and crop.")

        planting_date = self.validate_date(
            data.get("planting_date"), "Planting date"
        )
        expected_harvest_date = self.validate_date(
            data.get("expected_harvest_date"), "Expected harvest date"
        )

        if expected_harvest_date < planting_date:
            raise ValueError(
                "Harvest date cannot be earlier than planting date."
            )

        status = self.validate_text(data.get("status"), "Status")

        if status not in ["Growing", "Harvested", "Cancelled"]:
            raise ValueError("Invalid planting cycle status.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT pc.cycle_id
                FROM planting_cycles pc
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE pc.cycle_id = %s AND fm.farmer_id = %s
                """,
                (cycle_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Planting cycle not found."
                }

            cursor.execute(
                """
                SELECT f.field_id
                FROM fields f
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE f.field_id = %s AND fm.farmer_id = %s
                """,
                (field_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Selected field does not belong to you."
                }

            cursor.execute(
                """
                SELECT crop_id FROM crops
                WHERE crop_id = %s AND is_active = 1
                """,
                (crop_id,)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Selected crop is not available."
                }

            cursor.execute(
                """
                UPDATE planting_cycles
                SET field_id = %s,
                    crop_id = %s,
                    planting_date = %s,
                    expected_harvest_date = %s,
                    status = %s
                WHERE cycle_id = %s
                """,
                (
                    field_id, crop_id, planting_date,
                    expected_harvest_date, status, cycle_id
                )
            )

            connection.commit()

            return {
                "success": True,
                "message": "Planting cycle updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_planting_cycle(self, farmer_id, cycle_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE pc
                FROM planting_cycles pc
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE pc.cycle_id = %s AND fm.farmer_id = %s
                """,
                (cycle_id, farmer_id)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Planting cycle not found."
                }

            return {
                "success": True,
                "message": "Planting cycle deleted successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    
    # =================================
    # FARMING ACTIVITIES MANAGEMENT
    # =================================

    def farmer_owns_cycle(self, cursor, farmer_id, cycle_id):
        cursor.execute(
            """
            SELECT pc.cycle_id
            FROM planting_cycles pc
            JOIN fields f ON pc.field_id = f.field_id
            JOIN farms fm ON f.farm_id = fm.farm_id
            WHERE pc.cycle_id = %s
              AND fm.farmer_id = %s
            """,
            (cycle_id, farmer_id)
        )

        return cursor.fetchone() is not None

    def get_farmer_activities(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    a.activity_id,
                    a.cycle_id,
                    a.activity_type,
                    a.activity_date,
                    a.description,
                    a.cost,
                    c.crop_name,
                    f.field_name,
                    fm.farm_name
                FROM farming_activities a
                JOIN planting_cycles pc
                    ON a.cycle_id = pc.cycle_id
                JOIN fields f
                    ON pc.field_id = f.field_id
                JOIN farms fm
                    ON f.farm_id = fm.farm_id
                JOIN crops c
                    ON pc.crop_id = c.crop_id
                WHERE fm.farmer_id = %s
                ORDER BY a.activity_date DESC, a.activity_id DESC
                """,
                (farmer_id,)
            )

            activities = []

            for row in cursor.fetchall():
                activities.append({
                    "activity_id": row[0],
                    "cycle_id": row[1],
                    "activity_type": row[2],
                    "activity_date": str(row[3]) if row[3] else None,
                    "description": row[4] or "",
                    "cost": float(row[5] or 0),
                    "crop_name": row[6],
                    "field_name": row[7],
                    "farm_name": row[8]
                })

            return {
                "success": True,
                "activities": activities
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_activity(self, farmer_id, data):
        try:
            cycle_id = int(data.get("cycle_id"))

            if cycle_id <= 0:
                raise ValueError()

        except (TypeError, ValueError):
            raise ValueError("Please select a valid planting cycle.")

        activity_type = self.validate_activity_type(
            data.get("activity_type")
        )

        activity_date = self.validate_date(
            data.get("activity_date"), "Activity date"
        )

        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid activity description.")

        cost = self.validate_activity_cost(
            data.get("cost")
        )

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            if not self.farmer_owns_cycle(
                cursor, farmer_id, cycle_id
            ):
                return {
                    "success": False,
                    "message": "Selected planting cycle does not belong to you."
                }

            cursor.execute(
                """
                INSERT INTO farming_activities (
                    cycle_id,
                    activity_type,
                    activity_date,
                    description,
                    cost
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    cycle_id,
                    activity_type,
                    activity_date,
                    description.strip(),
                    cost
                )
            )

            activity_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Farming activity added successfully.",
                "activity_id": activity_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_activity(self, farmer_id, activity_id, data):
        try:
            cycle_id = int(data.get("cycle_id"))

            if cycle_id <= 0:
                raise ValueError()

        except (TypeError, ValueError):
            raise ValueError("Please select a valid planting cycle.")

        activity_type = self.validate_activity_type(
            data.get("activity_type")
        )

        activity_date = self.validate_date(
            data.get("activity_date"), "Activity date"
        )

        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid activity description.")

        cost = self.validate_activity_cost(
            data.get("cost")
        )

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT a.activity_id
                FROM farming_activities a
                JOIN planting_cycles pc
                    ON a.cycle_id = pc.cycle_id
                JOIN fields f
                    ON pc.field_id = f.field_id
                JOIN farms fm
                    ON f.farm_id = fm.farm_id
                WHERE a.activity_id = %s
                  AND fm.farmer_id = %s
                """,
                (activity_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Activity not found."
                }

            if not self.farmer_owns_cycle(
                cursor, farmer_id, cycle_id
            ):
                return {
                    "success": False,
                    "message": "Selected planting cycle does not belong to you."
                }

            cursor.execute(
                """
                UPDATE farming_activities
                SET cycle_id = %s,
                    activity_type = %s,
                    activity_date = %s,
                    description = %s,
                    cost = %s
                WHERE activity_id = %s
                """,
                (
                    cycle_id,
                    activity_type,
                    activity_date,
                    description.strip(),
                    cost,
                    activity_id
                )
            )

            connection.commit()

            return {
                "success": True,
                "message": "Farming activity updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_activity(self, farmer_id, activity_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE a
                FROM farming_activities a
                JOIN planting_cycles pc
                    ON a.cycle_id = pc.cycle_id
                JOIN fields f
                    ON pc.field_id = f.field_id
                JOIN farms fm
                    ON f.farm_id = fm.farm_id
                WHERE a.activity_id = %s
                  AND fm.farmer_id = %s
                """,
                (activity_id, farmer_id)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Activity not found."
                }

            return {
                "success": True,
                "message": "Farming activity deleted successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def get_farmer_expenses(self, farmer_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    e.expense_id,
                    e.cycle_id,
                    e.expense_type,
                    e.expense_date,
                    e.description,
                    e.amount,
                    c.crop_name,
                    f.field_name,
                    fm.farm_name
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                JOIN crops c ON pc.crop_id = c.crop_id
                WHERE fm.farmer_id = %s
                ORDER BY e.expense_date DESC, e.expense_id DESC
                """,
                (farmer_id,)
            )

            expenses = []

            for row in cursor.fetchall():
                expenses.append({
                    "expense_id": row[0],
                    "cycle_id": row[1],
                    "expense_type": row[2],
                    "expense_date": str(row[3]) if row[3] else None,
                    "description": row[4] or "",
                    "amount": float(row[5] or 0),
                    "crop_name": row[6],
                    "field_name": row[7],
                    "farm_name": row[8]
                })

            return {
                "success": True,
                "expenses": expenses
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def create_expense(self, farmer_id, data):
        try:
            cycle_id = int(data.get("cycle_id"))

            if cycle_id <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Please select a valid planting cycle.")

        expense_type = self.validate_expense_type(
            data.get("expense_type")
        )
        expense_date = self.validate_date(
            data.get("expense_date"), "Expense date"
        )
        amount = self.validate_expense_amount(data.get("amount"))
        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid expense description.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            if not self.farmer_owns_cycle(cursor, farmer_id, cycle_id):
                return {
                    "success": False,
                    "message": "Selected planting cycle does not belong to you."
                }

            cursor.execute(
                """
                INSERT INTO expenses (
                    cycle_id, expense_type, expense_date,
                    description, amount
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    cycle_id, expense_type, expense_date,
                    description.strip(), amount
                )
            )

            expense_id = cursor.lastrowid
            connection.commit()

            return {
                "success": True,
                "message": "Expense added successfully.",
                "expense_id": expense_id
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_expense(self, farmer_id, expense_id, data):
        try:
            cycle_id = int(data.get("cycle_id"))

            if cycle_id <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Please select a valid planting cycle.")

        expense_type = self.validate_expense_type(
            data.get("expense_type")
        )
        expense_date = self.validate_date(
            data.get("expense_date"), "Expense date"
        )
        amount = self.validate_expense_amount(data.get("amount"))
        description = data.get("description", "")

        if not isinstance(description, str):
            raise ValueError("Invalid expense description.")

        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT e.expense_id
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE e.expense_id = %s AND fm.farmer_id = %s
                """,
                (expense_id, farmer_id)
            )

            if cursor.fetchone() is None:
                return {
                    "success": False,
                    "message": "Expense not found."
                }

            if not self.farmer_owns_cycle(cursor, farmer_id, cycle_id):
                return {
                    "success": False,
                    "message": "Selected planting cycle does not belong to you."
                }

            cursor.execute(
                """
                UPDATE expenses
                SET cycle_id = %s,
                    expense_type = %s,
                    expense_date = %s,
                    description = %s,
                    amount = %s
                WHERE expense_id = %s
                """,
                (
                    cycle_id, expense_type, expense_date,
                    description.strip(), amount, expense_id
                )
            )

            connection.commit()

            return {
                "success": True,
                "message": "Expense updated successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def delete_expense(self, farmer_id, expense_id):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE e
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE e.expense_id = %s AND fm.farmer_id = %s
                """,
                (expense_id, farmer_id)
            )

            deleted = cursor.rowcount
            connection.commit()

            if deleted == 0:
                return {
                    "success": False,
                    "message": "Expense not found."
                }

            return {
                "success": True,
                "message": "Expense deleted successfully."
            }

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # =================================
    # REPORTS & ANALYTICS
    # =================================

    # DATE FILTER HELPER

    def get_report_date_filter(self):
        params = parse_qs(urlparse(self.path).query)

        start_value = params.get("start_date", [None])[0]
        end_value = params.get("end_date", [None])[0]

        if not start_value and not end_value:
            return None, None

        if not start_value or not end_value:
            raise ValueError(
                "Please select both start date and end date."
            )

        start_date = self.validate_date(start_value, "Start date")
        end_date = self.validate_date(end_value, "End date")

        if start_date > end_date:
            raise ValueError(
                "Start date cannot be later than end date."
            )

        return start_date, end_date

    # 1. REPORT SUMMARY

    def get_report_summary(self, farmer_id, start_date=None, end_date=None):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            expense_filter = ""
            expense_params = []

            if start_date and end_date:
                expense_filter = """
                    AND e.expense_date BETWEEN %s AND %s
                """
                expense_params = [start_date, end_date]

            cursor.execute(
                f"""
                SELECT
                    (SELECT COUNT(*)
                     FROM farms
                     WHERE farmer_id = %s),

                    (SELECT COUNT(*)
                     FROM fields f
                     JOIN farms fm ON f.farm_id = fm.farm_id
                     WHERE fm.farmer_id = %s),

                    (SELECT COUNT(*)
                     FROM planting_cycles pc
                     JOIN fields f ON pc.field_id = f.field_id
                     JOIN farms fm ON f.farm_id = fm.farm_id
                     WHERE fm.farmer_id = %s),

                    (SELECT COALESCE(SUM(e.amount), 0)
                     FROM expenses e
                     JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                     JOIN fields f ON pc.field_id = f.field_id
                     JOIN farms fm ON f.farm_id = fm.farm_id
                     WHERE fm.farmer_id = %s
                     {expense_filter}),

                    (SELECT COUNT(*)
                     FROM expenses e
                     JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                     JOIN fields f ON pc.field_id = f.field_id
                     JOIN farms fm ON f.farm_id = fm.farm_id
                     WHERE fm.farmer_id = %s
                     {expense_filter})
                """,
                (
                    farmer_id,
                    farmer_id,
                    farmer_id,
                    farmer_id,
                    *expense_params,
                    farmer_id,
                    *expense_params
                )
            )

            row = cursor.fetchone()

            return {
                "success": True,
                "summary": {
                    "total_farms": int(row[0] or 0),
                    "total_fields": int(row[1] or 0),
                    "total_planting_cycles": int(row[2] or 0),
                    "total_expenses": float(row[3] or 0),
                    "expense_count": int(row[4] or 0)
                }
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # 2. CATEGORY-WISE EXPENSE REPORT

    def get_expense_category_report(
        self, farmer_id, start_date=None, end_date=None
    ):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            date_filter = ""
            params = [farmer_id]

            if start_date and end_date:
                date_filter = """
                    AND e.expense_date BETWEEN %s AND %s
                """
                params.extend([start_date, end_date])

            cursor.execute(
                f"""
                SELECT
                    e.expense_type,
                    COALESCE(SUM(e.amount), 0),
                    COUNT(e.expense_id)
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                {date_filter}
                GROUP BY e.expense_type
                ORDER BY SUM(e.amount) DESC
                """,
                tuple(params)
            )

            categories = []

            for row in cursor.fetchall():
                categories.append({
                    "expense_type": row[0],
                    "total_amount": float(row[1] or 0),
                    "expense_count": int(row[2] or 0)
                })

            return {
                "success": True,
                "categories": categories
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # 3. MONTHLY EXPENSE REPORT

    def get_monthly_expense_report(
        self, farmer_id, start_date=None, end_date=None
    ):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            date_filter = ""
            params = [farmer_id]

            if start_date and end_date:
                date_filter = """
                    AND e.expense_date BETWEEN %s AND %s
                """
                params.extend([start_date, end_date])

            cursor.execute(
                f"""
                SELECT
                    DATE_FORMAT(e.expense_date, '%Y-%m'),
                    COALESCE(SUM(e.amount), 0),
                    COUNT(e.expense_id)
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                {date_filter}
                GROUP BY DATE_FORMAT(e.expense_date, '%Y-%m')
                ORDER BY DATE_FORMAT(e.expense_date, '%Y-%m')
                """,
                tuple(params)
            )

            monthly = []

            for row in cursor.fetchall():
                monthly.append({
                    "month": row[0],
                    "total_amount": float(row[1] or 0),
                    "expense_count": int(row[2] or 0)
                })

            return {
                "success": True,
                "monthly": monthly
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # 4. CROP-WISE EXPENSE REPORT

    def get_crop_expense_report(
        self, farmer_id, start_date=None, end_date=None
    ):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            date_filter = ""
            params = [farmer_id]

            if start_date and end_date:
                date_filter = """
                    AND e.expense_date BETWEEN %s AND %s
                """
                params.extend([start_date, end_date])

            cursor.execute(
                f"""
                SELECT
                    c.crop_name,
                    COALESCE(SUM(e.amount), 0),
                    COUNT(e.expense_id)
                FROM expenses e
                JOIN planting_cycles pc ON e.cycle_id = pc.cycle_id
                JOIN crops c ON pc.crop_id = c.crop_id
                JOIN fields f ON pc.field_id = f.field_id
                JOIN farms fm ON f.farm_id = fm.farm_id
                WHERE fm.farmer_id = %s
                {date_filter}
                GROUP BY c.crop_id, c.crop_name
                ORDER BY SUM(e.amount) DESC
                """,
                tuple(params)
            )

            crops = []

            for row in cursor.fetchall():
                crops.append({
                    "crop_name": row[0],
                    "total_amount": float(row[1] or 0),
                    "expense_count": int(row[2] or 0)
                })

            return {
                "success": True,
                "crops": crops
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # 5. FARM-WISE EXPENSE REPORT

    def get_farm_expense_report(
        self, farmer_id, start_date=None, end_date=None
    ):
        connection = None
        cursor = None

        try:
            connection = self.get_db()
            cursor = connection.cursor()

            date_filter = ""
            params = []

            if start_date and end_date:
                date_filter = """
                    AND e.expense_date BETWEEN %s AND %s
                """
                params.extend([start_date, end_date])

            params.append(farmer_id)

            cursor.execute(
                f"""
                SELECT
                    fm.farm_name,
                    COALESCE(SUM(e.amount), 0),
                    COUNT(e.expense_id)
                FROM farms fm
                LEFT JOIN fields f ON fm.farm_id = f.farm_id
                LEFT JOIN planting_cycles pc ON f.field_id = pc.field_id
                LEFT JOIN expenses e
                    ON pc.cycle_id = e.cycle_id
                    {date_filter}
                WHERE fm.farmer_id = %s
                GROUP BY fm.farm_id, fm.farm_name
                ORDER BY SUM(e.amount) DESC
                """,
                tuple(params)
            )

            farms = []

            for row in cursor.fetchall():
                farms.append({
                    "farm_name": row[0],
                    "total_amount": float(row[1] or 0),
                    "expense_count": int(row[2] or 0)
                })

            return {
                "success": True,
                "farms": farms
            }

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        # =================================
    # GET REQUEST
    # ============================
    def do_GET(self):
        path = urlparse(self.path).path


      # SERVER STATUS
        if path == "/api/status":
            self.send_json({
                "success": True,
                "message": "Smart Agriculture Server is running!"
            })
            return
        

        # ADMIN SESSION CHECK

        # =================================
        # ADMIN DASHBOARD STATISTICS
        # =================================

        if path == "/api/admin/dashboard-stats":

            admin = self.require_admin()

            if admin is None:
                return

            connection = get_connection()

            if connection is None:
                self.send_json({
                    "success": False,
                    "message": "Database connection failed."
                }, status=500)
                return

            cursor = connection.cursor()

            try:
                statistics = {}

                tables = {
                    "total_farmers": "farmers",
                    "total_farms": "farms",
                    "total_fields": "fields",
                    "total_crops": "crops",
                    "total_planting_cycles": "planting_cycles",
                    "total_expenses": "expenses"
                }

                for key, table in tables.items():

                    cursor.execute(
                        f"SELECT COUNT(*) FROM `{table}`"
                    )

                    statistics[key] = cursor.fetchone()[0]

                self.send_json({
                    "success": True,
                    "statistics": statistics
                })

            except Exception as error:

                print("Admin dashboard statistics error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load dashboard statistics."
                }, status=500)

            finally:
                cursor.close()
                connection.close()

            return

        
        # =================================

        # =================================
        # ADMIN - ALL FARMERS
        # =================================

        if path == "/api/admin/farmers":

            admin = self.require_admin()

            if admin is None:
                return

            connection = get_connection()

            if connection is None:
                self.send_json({
                    "success": False,
                    "message": "Database connection failed."
                }, status=500)
                return

            cursor = connection.cursor()

            try:
                query = """
                    SELECT
                        farmer_id,
                        full_name,
                        email,
                        phone,
                        created_at
                    FROM farmers
                    ORDER BY farmer_id DESC
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                farmers = []

                for row in rows:
                    farmers.append({
                        "farmer_id": row[0],
                        "full_name": row[1],
                        "email": row[2],
                        "phone": row[3] or "N/A",
                        "created_at": (
                            str(row[4]) if row[4] else "N/A"
                        )
                    })

                self.send_json({
                    "success": True,
                    "total_farmers": len(farmers),
                    "farmers": farmers
                })

            except Exception as error:
                print("Admin farmers error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load farmers."
                }, status=500)

            finally:
                cursor.close()
                connection.close()

            return
            
        # =================================
        # ADMIN - FARMER DETAILS
        # =================================

        if path == "/api/admin/farmer-details":

            admin = self.require_admin()

            if admin is None:
                return

            query_params = parse_qs(urlparse(self.path).query)

            farmer_id_values = query_params.get("farmer_id", [])

            if not farmer_id_values:
                self.send_json({
                    "success": False,
                    "message": "Farmer ID is required."
                }, status=400)
                return

            try:
                farmer_id = int(farmer_id_values[0])

                if farmer_id <= 0:
                    raise ValueError

            except ValueError:
                self.send_json({
                    "success": False,
                    "message": "Invalid Farmer ID."
                }, status=400)
                return

            connection = get_connection()

            if connection is None:
                self.send_json({
                    "success": False,
                    "message": "Database connection failed."
                }, status=500)
                return

            cursor = connection.cursor()

            try:
                # 1. Farmer Information
                cursor.execute("""
                    SELECT
                        farmer_id,
                        full_name,
                        email,
                        phone,
                        created_at
                    FROM farmers
                    WHERE farmer_id = %s
                """, (farmer_id,))

                farmer = cursor.fetchone()

                if farmer is None:
                    self.send_json({
                        "success": False,
                        "message": "Farmer not found."
                    }, status=404)
                    return

                # 2. Total Farms
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM farms
                    WHERE farmer_id = %s
                """, (farmer_id,))

                total_farms = cursor.fetchone()[0]

                # 3. Total Fields
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM fields f
                    JOIN farms fa ON f.farm_id = fa.farm_id
                    WHERE fa.farmer_id = %s
                """, (farmer_id,))

                total_fields = cursor.fetchone()[0]

                # 4. Total Planting Cycles
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM planting_cycles pc
                    JOIN fields f ON pc.field_id = f.field_id
                    JOIN farms fa ON f.farm_id = fa.farm_id
                    WHERE fa.farmer_id = %s
                """, (farmer_id,))

                total_cycles = cursor.fetchone()[0]

                # 5. Total Expenses
                cursor.execute("""
                    SELECT COALESCE(SUM(e.amount), 0)
                    FROM expenses e
                    JOIN planting_cycles pc
                        ON e.cycle_id = pc.cycle_id
                    JOIN fields f
                        ON pc.field_id = f.field_id
                    JOIN farms fa
                        ON f.farm_id = fa.farm_id
                    WHERE fa.farmer_id = %s
                """, (farmer_id,))

                total_expenses = cursor.fetchone()[0]

                # 6. Farm and Field Information
                cursor.execute("""
                    SELECT
                        fa.farm_id,
                        fa.farm_name,
                        fa.district,
                        fa.latitude,
                        fa.longitude,
                        f.field_id,
                        f.field_name,
                        f.area_acres,
                        f.soil_type,
                        f.soil_ph
                    FROM farms fa
                    LEFT JOIN fields f
                        ON fa.farm_id = f.farm_id
                    WHERE fa.farmer_id = %s
                    ORDER BY fa.farm_id DESC, f.field_id DESC
                """, (farmer_id,))

                farm_rows = cursor.fetchall()

                farms = {}

                for row in farm_rows:

                    farm_id = row[0]

                    if farm_id not in farms:
                        farms[farm_id] = {
                            "farm_id": farm_id,
                            "farm_name": row[1],
                            "district": row[2],
                            "latitude": float(row[3]) if row[3] is not None else None,
                            "longitude": float(row[4]) if row[4] is not None else None,
                            "fields": []
                        }

                    if row[5] is not None:
                        farms[farm_id]["fields"].append({
                            "field_id": row[5],
                            "field_name": row[6],
                            "area_acres": float(row[7]) if row[7] is not None else 0,
                            "soil_type": row[8] or "N/A",
                            "soil_ph": float(row[9]) if row[9] is not None else None
                        })

                # 7. Final Response
                print("DEBUG: FARMER DETAILS V2 CODE IS RUNNING")
                self.send_json({
                    "success": True,

                    "farmer": {
                        "farmer_id": farmer[0],
                        "full_name": farmer[1],
                        "email": farmer[2],
                        "phone": farmer[3] or "N/A",
                        "created_at": str(farmer[4]) if farmer[4] else "N/A"
                    },

                    "statistics": {
                        "total_farms": int(total_farms or 0),
                        "total_fields": int(total_fields or 0),
                        "total_planting_cycles": int(total_cycles or 0),
                        "total_expenses": float(total_expenses or 0)
                    },

                    "farms": list(farms.values()),
                    "debug_marker": "farmer_details_v2"
                })

            except Exception as error:
                print("Farmer details error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load farmer details."
                }, status=500)

            finally:
                cursor.close()
                connection.close()

            return


        if path == "/api/admin/me":

            admin = self.require_admin()

            if admin is None:
                return

            self.send_json({
                "success": True,
                "admin": admin
            })

            return

        # FARMER SESSION CHECK
        if path == "/api/me":

            farmer = self.require_farmer()

            if farmer is None:
                return

            self.send_json({
                "success": True,
                "farmer": farmer
            })

            return

        # DASHBOARD STATISTICS
        if path == "/api/dashboard-stats":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_dashboard_statistics(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Dashboard statistics error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load dashboard statistics."
                }, status=500)

            return

        # FARMS
        if path == "/api/farms":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_farmer_farms(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Get farms error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load farms."
                }, status=500)

            return

        # FIELDS
        if path == "/api/fields":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_farmer_fields(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Get fields error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load fields."
                }, status=500)

            return

        # CROPS
        if path == "/api/crops":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_all_crops()
                self.send_json(result)

            except Exception as error:
                print("Get crops error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load crops."
                }, status=500)

            return

        # PLANTING CYCLES
        if path == "/api/planting-cycles":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_planting_cycles(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Get planting cycles error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load planting cycles."
                }, status=500)

            return

        # FARMING ACTIVITIES
        if path == "/api/activities":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_farmer_activities(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Get activities error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load farming activities."
                }, status=500)

            return

        # EXPENSES
        if path == "/api/expenses":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.get_farmer_expenses(
                    farmer["farmer_id"]
                )

                self.send_json(result)

            except Exception as error:
                print("Get expenses error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to load expenses."
                }, status=500)

            return

        # REPORTS API
        if path.startswith("/api/reports/"):

            farmer = self.require_farmer()

            if farmer is None:
                return

            farmer_id = farmer["farmer_id"]

            try:
                start_date, end_date = self.get_report_date_filter()

                if path == "/api/reports/summary":

                    result = self.get_report_summary(
                        farmer_id, start_date, end_date
                    )

                elif path == "/api/reports/category":

                    result = self.get_expense_category_report(
                        farmer_id, start_date, end_date
                    )

                elif path == "/api/reports/monthly":

                    result = self.get_monthly_expense_report(
                        farmer_id, start_date, end_date
                    )

                elif path == "/api/reports/crop":

                    result = self.get_crop_expense_report(
                        farmer_id, start_date, end_date
                    )

                elif path == "/api/reports/farm":

                    result = self.get_farm_expense_report(
                        farmer_id, start_date, end_date
                    )

                else:

                    self.send_json({
                        "success": False,
                        "message": "Report endpoint not found."
                    }, status=404)

                    return

                self.send_json(result)

            except ValueError as error:

                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:

                print("Reports error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to generate report."
                }, status=500)

            return

        # DEFAULT FILE / PAGE HANDLER
        super().do_GET()
    # =================================
    # POST REQUEST
    # =================================

    
    # =================================
    # POST REQUEST
    # =================================

    def do_POST(self):
        path = urlparse(self.path).path

        try:
            data = self.read_json()
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            ValueError
        ):
            self.send_json({
                "success": False,
                "message": "Invalid request data."
            }, status=400)
            return

        # =================================
        # ADMIN LOGIN
        # =================================

        if path == "/api/admin/login":

            email = data.get("email", "")
            password = data.get("password", "")

            if not isinstance(email, str) or not isinstance(password, str):
                self.send_json({
                    "success": False,
                    "message": "Invalid login information."
                }, status=400)
                return

            email = email.strip().lower()

            if not email or not password:
                self.send_json({
                    "success": False,
                    "message": "Email and password are required."
                }, status=400)
                return

            try:
                admin = login_admin(email, password)

                if admin is None:
                    self.send_json({
                        "success": False,
                        "message": "Invalid admin email or password."
                    }, status=401)
                    return

                token = secrets.token_urlsafe(32)
                active_admin_sessions[token] = admin

                self.send_json(
                    {
                        "success": True,
                        "message": "Admin login successful.",
                        "admin": admin
                    },
                    headers={
                        "Set-Cookie": (
                            f"admin_session={token}; "
                            "HttpOnly; Path=/; SameSite=Lax"
                        )
                    }
                )

            except Exception as error:
                print("Admin login error:", error)

                self.send_json({
                    "success": False,
                    "message": "Admin login failed."
                }, status=500)

            return

        # =================================
        # ADMIN LOGOUT
        # =================================

        if path == "/api/admin/logout":

            token = self.get_admin_session_token()

            if token:
                active_admin_sessions.pop(token, None)

            self.send_json(
                {
                    "success": True,
                    "message": "Admin logout successful."
                },
                headers={
                    "Set-Cookie": (
                        "admin_session=; "
                        "HttpOnly; Path=/; "
                        "SameSite=Lax; Max-Age=0"
                    )
                }
            )

            return

        # =================================
        # API TEST
        # =================================

        if path == "/api/test":
            self.send_json({
                "success": True,
                "message": "API connection successful!",
                "received_data": data
            })
            return

        # =================================
        # FARMER REGISTRATION
        # =================================

        if path == "/api/register":

            name = data.get("name", "")
            email = data.get("email", "")
            phone = data.get("phone", "")
            password = data.get("password", "")

            if not all(
                isinstance(value, str)
                for value in [name, email, phone, password]
            ):
                self.send_json({
                    "success": False,
                    "message": "Invalid field values."
                }, status=400)
                return

            name = name.strip()
            email = email.strip()
            phone = phone.strip()

            if not name or not email or not password:
                self.send_json({
                    "success": False,
                    "message": "Please fill in all required fields."
                }, status=400)
                return

            if len(password) < 8:
                self.send_json({
                    "success": False,
                    "message": "Password must be at least 8 characters."
                }, status=400)
                return

            try:
                farmer_id = register_farmer(
                    name, email, phone, password
                )

                if farmer_id:
                    self.send_json({
                        "success": True,
                        "message": "Registration successful!",
                        "farmer_id": farmer_id
                    }, status=201)
                else:
                    self.send_json({
                        "success": False,
                        "message": "Registration failed. Email may already exist."
                    }, status=400)

            except Exception as error:
                print("Registration error:", error)

                self.send_json({
                    "success": False,
                    "message": "Registration failed."
                }, status=500)

            return

        # =================================
        # FARMER LOGIN
        # =================================

        if path == "/api/login":

            email = data.get("email", "")
            password = data.get("password", "")

            if not isinstance(email, str) or not isinstance(password, str):
                self.send_json({
                    "success": False,
                    "message": "Invalid login information."
                }, status=400)
                return

            email = email.strip()

            if not email or not password:
                self.send_json({
                    "success": False,
                    "message": "Email and password are required."
                }, status=400)
                return

            try:
                farmer_id = login_farmer(email, password)

                if farmer_id:
                    token = secrets.token_urlsafe(32)

                    active_sessions[token] = {
                        "farmer_id": farmer_id,
                        "email": email
                    }

                    self.send_json(
                        {
                            "success": True,
                            "message": "Login successful!",
                            "farmer_id": farmer_id
                        },
                        headers={
                            "Set-Cookie": (
                                f"farmer_session={token}; "
                                "HttpOnly; Path=/; SameSite=Lax"
                            )
                        }
                    )

                else:
                    self.send_json({
                        "success": False,
                        "message": "Invalid email or password."
                    }, status=401)

            except Exception as error:
                print("Login error:", error)

                self.send_json({
                    "success": False,
                    "message": "Login failed."
                }, status=500)

            return

        # =================================
        # FARMER LOGOUT
        # =================================

        if path == "/api/logout":

            token = self.get_session_token()

            if token:
                active_sessions.pop(token, None)

            self.send_json(
                {
                    "success": True,
                    "message": "Logged out successfully!"
                },
                headers={
                    "Set-Cookie": (
                        "farmer_session=; "
                        "HttpOnly; Path=/; "
                        "SameSite=Lax; Max-Age=0"
                    )
                }
            )

            return

        # =================================
        # CREATE FARM
        # =================================

        if path == "/api/farms":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_farm(
                    farmer["farmer_id"], data
                )

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create farm error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to create farm."
                }, status=500)

            return

        # =================================
        # CREATE FIELD
        # =================================

        if path == "/api/fields":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_field(
                    farmer["farmer_id"], data
                )

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create field error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to create field."
                }, status=500)

            return

        # =================================
        # CREATE CROP
        # =================================

        if path == "/api/crops":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_crop(data)

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create crop error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to add crop."
                }, status=500)

            return

        # =================================
        # CREATE PLANTING CYCLE
        # =================================

        if path == "/api/planting-cycles":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_planting_cycle(
                    farmer["farmer_id"], data
                )

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create planting cycle error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to create planting cycle."
                }, status=500)

            return

        # =================================
        # CREATE FARMING ACTIVITY
        # =================================

        if path == "/api/activities":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_activity(
                    farmer["farmer_id"], data
                )

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create activity error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to create farming activity."
                }, status=500)

            return

        # =================================
        # CREATE EXPENSE
        # =================================

        if path == "/api/expenses":

            farmer = self.require_farmer()

            if farmer is None:
                return

            try:
                result = self.create_expense(
                    farmer["farmer_id"], data
                )

                self.send_json(
                    result,
                    status=201 if result["success"] else 400
                )

            except ValueError as error:
                self.send_json({
                    "success": False,
                    "message": str(error)
                }, status=400)

            except Exception as error:
                print("Create expense error:", error)

                self.send_json({
                    "success": False,
                    "message": "Unable to create expense."
                }, status=500)

            return

        # =================================
        # UNKNOWN API
        # =================================

        self.send_json({
            "success": False,
            "message": "API endpoint not found."
        }, status=404)

    # PUT REQUEST
    # =================================

    def do_PUT(self):
        path = urlparse(self.path).path

        try:
            data = self.read_json()
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            ValueError
        ):
            self.send_json({
                "success": False,
                "message": "Invalid request data."
            }, status=400)
            return

        farmer = self.require_farmer()

        if farmer is None:
            return

        farmer_id = farmer["farmer_id"]
        parts = path.strip("/").split("/")

        if len(parts) != 3 or parts[0] != "api":
            self.send_json({
                "success": False,
                "message": "API endpoint not found."
            }, status=404)
            return

        resource = parts[1]

        try:
            item_id = int(parts[2])

            if item_id <= 0:
                raise ValueError()

        except ValueError:
            self.send_json({
                "success": False,
                "message": "Invalid ID."
            }, status=400)
            return

        try:
            if resource == "farms":
                result = self.update_farm(
                    farmer_id, item_id, data
                )

            elif resource == "fields":
                result = self.update_field(
                    farmer_id, item_id, data
                )

            elif resource == "crops":
                result = self.update_crop(item_id, data)

            elif resource == "planting-cycles":
                result = self.update_planting_cycle(
                    farmer_id, item_id, data
                )

            elif resource == "activities":
                result = self.update_activity(
                    farmer_id, item_id, data
                )

            elif resource == "expenses":
                result = self.update_expense(
                    farmer_id, item_id, data
                )

            else:
                self.send_json({
                    "success": False,
                    "message": "API endpoint not found."
                }, status=404)
                return

            self.send_json(
                result,
                status=200 if result["success"] else 404
            )

        except ValueError as error:
            self.send_json({
                "success": False,
                "message": str(error)
            }, status=400)

        except Exception as error:
            print("Update error:", error)

            self.send_json({
                "success": False,
                "message": "Unable to update record. Check related records and database constraints."
            }, status=500)

    # =================================
    # DELETE REQUEST
    # =================================

    def do_DELETE(self):
        path = urlparse(self.path).path

        farmer = self.require_farmer()

        if farmer is None:
            return

        farmer_id = farmer["farmer_id"]
        parts = path.strip("/").split("/")

        if len(parts) != 3 or parts[0] != "api":
            self.send_json({
                "success": False,
                "message": "API endpoint not found."
            }, status=404)
            return

        resource = parts[1]

        try:
            item_id = int(parts[2])

            if item_id <= 0:
                raise ValueError()

        except ValueError:
            self.send_json({
                "success": False,
                "message": "Invalid ID."
            }, status=400)
            return

        try:
            if resource == "farms":
                result = self.delete_farm(
                    farmer_id, item_id
                )

            elif resource == "fields":
                result = self.delete_field(
                    farmer_id, item_id
                )

            elif resource == "crops":
                result = self.delete_crop(item_id)

            elif resource == "planting-cycles":
                result = self.delete_planting_cycle(
                    farmer_id, item_id
                )

            elif resource == "activities":
                result = self.delete_activity(
                    farmer_id, item_id
                )

            elif resource == "expenses":
                result = self.delete_expense(
                    farmer_id, item_id
                )

            else:
                self.send_json({
                    "success": False,
                    "message": "API endpoint not found."
                }, status=404)
                return

            self.send_json(
                result,
                status=200 if result["success"] else 404
            )

        except Exception as error:
            print("Delete error:", error)

            self.send_json({
                "success": False,
                "message": "Unable to delete record. It may have related records."
            }, status=500)


# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":

    server = HTTPServer(
        (HOST, PORT),
        SmartAgricultureHandler
    )

    print("====================================")
    print(" SMART AGRICULTURE WEB SERVER")
    print("====================================")
    print(f"Server running at: http://{HOST}:{PORT}")
    print("Press CTRL + C to stop the server.")
    print("====================================")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.server_close()
