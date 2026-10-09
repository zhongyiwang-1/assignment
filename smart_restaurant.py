import csv
import math


# Approximate coordinates for supported suburbs
SUBURB_COORDINATES = {
    "sydney cbd": (-33.8688, 151.2093),
    "haymarket": (-33.8790, 151.2040),
    "chinatown": (-33.8770, 151.2060),
    "surry hills": (-33.8840, 151.2130)
}


def load_restaurants(filename):
    restaurants = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["average_price"] = int(row["average_price"])
            row["latitude"] = float(row["latitude"])
            row["longitude"] = float(row["longitude"])

            restaurants.append(row)

    return restaurants


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometres
    earth_radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    difference_lat = lat2 - lat1
    difference_lon = lon2 - lon1

    a = (
        math.sin(difference_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(difference_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c

    return distance


def get_user_preferences():
    print("\nPlease enter your restaurant preferences.")

    cuisine = input("Preferred cuisine: ").strip().lower()

    while True:
        try:
            budget = int(input("Maximum budget per person ($): "))

            if budget > 0:
                break
            else:
                print("Budget must be greater than 0.")

        except ValueError:
            print("Please enter a valid number.")

    print("\nAvailable suburbs:")
    for suburb in SUBURB_COORDINATES:
        print("-", suburb.title())

    while True:
        suburb = input("\nYour suburb: ").strip().lower()

        if suburb in SUBURB_COORDINATES:
            break

        print("Sorry, this suburb is not currently supported.")

    while True:
        try:
            max_distance = float(
                input("Maximum distance from your location (km): ")
            )

            if max_distance > 0:
                break
            else:
                print("Distance must be greater than 0.")

        except ValueError:
            print("Please enter a valid number.")

    return cuisine, budget, suburb, max_distance


def filter_restaurants(
    restaurants,
    cuisine,
    budget,
    suburb,
    max_distance
):
    matches = []

    user_latitude, user_longitude = SUBURB_COORDINATES[suburb]

    for restaurant in restaurants:

        restaurant_cuisine = restaurant["cuisine"].strip().lower()
        restaurant_price = restaurant["average_price"]

        distance = calculate_distance(
            user_latitude,
            user_longitude,
            restaurant["latitude"],
            restaurant["longitude"]
        )

        if (
            restaurant_cuisine == cuisine
            and restaurant_price <= budget
            and distance <= max_distance
        ):
            restaurant["distance"] = distance
            matches.append(restaurant)

    return matches


def display_results(matches):
    print("\n================================")
    print(" Matching Restaurants")
    print("================================")

    if len(matches) == 0:
        print("Sorry, no restaurants match your preferences.")
        return

    # Show closest restaurants first
    matches.sort(key=lambda restaurant: restaurant["distance"])

    print("Found", len(matches), "restaurant(s):\n")

    for number, restaurant in enumerate(matches, start=1):

        print(str(number) + ".", restaurant["name"])
        print("   Cuisine:", restaurant["cuisine"])
        print(
            "   Average price: $"
            + str(restaurant["average_price"])
        )
        print("   Suburb:", restaurant["suburb"])
        print(
            "   Distance:",
            round(restaurant["distance"], 2),
            "km"
        )
        print()


def main():
    print("========================================")
    print(" Smart Travelling Restaurant Finder")
    print("========================================")

    restaurants = load_restaurants("restaurants.csv")

    print("Restaurant data loaded successfully.")
    print("Total restaurants:", len(restaurants))

    cuisine, budget, suburb, max_distance = get_user_preferences()

    matches = filter_restaurants(
        restaurants,
        cuisine,
        budget,
        suburb,
        max_distance
    )

    display_results(matches)


if __name__ == "__main__":
    main()