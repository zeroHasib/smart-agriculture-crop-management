
from crop_recommendation import recommend_crops

district = input("Enter district: ")
upazila = input("Enter upazila: ")

print("\nSelect Season")
print("1. Rabi")
print("2. Kharif-1")
print("3. Kharif-2")

choice = input("Enter choice: ")

seasons = {
    "1": "Rabi",
    "2": "Kharif-1",
    "3": "Kharif-2"
}

season = seasons.get(choice)

if season:
    recommend_crops(district, upazila, season)
else:
    print("Invalid season selection!")
