import csv
import math
import tkinter as tk
from tkinter import ttk, messagebox

# Coordinates used for distance calculations
SUBURB_COORDINATES = {
    "sydney cbd": (-33.8688, 151.2093),
    "haymarket": (-33.8793, 151.2050),
    "chinatown": (-33.8774, 151.2056),
    "surry hills": (-33.8844, 151.2122)
}

# Load restaurant data from the CSV file
def load_restaurants(filename):
    restaurants = []
    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                row["average_price"] = float(row["average_price"])
                row["latitude"] = float(row["latitude"])
                row["longitude"] = float(row["longitude"])
                row["rating"] = float(row["rating"])
                restaurants.append(row)
    except FileNotFoundError:
        messagebox.showerror("File Error", "restaurants.csv could not be found.")
    return restaurants

# Calculate distance between two locations in kilometres
def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    difference_lat = lat2 - lat1
    difference_lon = lon2 - lon1
    a = (math.sin(difference_lat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2)
         * math.sin(difference_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius * c

# Filter restaurants using the user's preferences
def filter_restaurants(restaurants, cuisine, budget, suburb,
                       max_distance, minimum_rating, dietary):
    matches = []
    user_lat, user_lon = SUBURB_COORDINATES[suburb]

    for restaurant in restaurants:
        distance = calculate_distance(
            user_lat, user_lon,
            restaurant["latitude"], restaurant["longitude"]
        )
        cuisine_match = (cuisine == "any"
            or restaurant["cuisine"].strip().lower() == cuisine)
        dietary_match = (dietary == "any"
            or restaurant["dietary"].strip().lower() == dietary)

        if (cuisine_match
                and restaurant["average_price"] <= budget
                and distance <= max_distance
                and restaurant["rating"] >= minimum_rating
                and dietary_match):
            result = restaurant.copy()
            result["distance"] = distance
            matches.append(result)
    return matches

# Sort the matching restaurants
def sort_restaurants(restaurants, sort_by):
    if sort_by == "Distance":
        restaurants.sort(key=lambda item: item["distance"])
    elif sort_by == "Rating":
        restaurants.sort(key=lambda item: item["rating"], reverse=True)
    elif sort_by == "Price":
        restaurants.sort(key=lambda item: item["average_price"])
    return restaurants

# Main graphical user interface
class RestaurantFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Travelling Restaurant Finder")
        self.root.geometry("800x680")
        self.restaurants = load_restaurants("restaurants.csv")
        self.build_interface()

    def add_dropdown(self, frame, label, variable, values, row, column):
        ttk.Label(frame, text=label).grid(
            row=row, column=column, sticky="w", padx=8)
        ttk.Combobox(
            frame, textvariable=variable, values=values, state="readonly"
        ).grid(row=row+1, column=column, sticky="ew",
               padx=8, pady=(4, 12))

# Create the labels, inputs and buttons
    def build_interface(self):
        ttk.Label(
            self.root, text="Smart Travelling Restaurant Finder",
            font=("Arial", 21, "bold")
        ).pack(pady=(20, 5))
        ttk.Label(
            self.root,
            text="Choose your preferences to find suitable restaurants."
        ).pack(pady=(0, 15))

        form = ttk.Frame(self.root)
        form.pack(fill="x", padx=30)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.suburb_var = tk.StringVar(value="Haymarket")
        self.cuisine_var = tk.StringVar(value="Any")
        self.budget_var = tk.StringVar(value="40")
        self.distance_var = tk.StringVar(value="3")
        self.rating_var = tk.StringVar(value="Any")
        self.dietary_var = tk.StringVar(value="Any")
        self.sort_var = tk.StringVar(value="Distance")

        self.add_dropdown(form, "Your Suburb", self.suburb_var,
            ["Sydney CBD", "Haymarket", "Chinatown", "Surry Hills"], 0, 0)
        self.add_dropdown(form, "Preferred Cuisine", self.cuisine_var,
            ["Any", "Japanese", "Chinese", "Korean", "Thai",
             "Italian", "Vietnamese", "Vegetarian"], 0, 1)

        ttk.Label(form, text="Maximum Budget ($ per person)").grid(
            row=2, column=0, sticky="w", padx=8)
        ttk.Entry(form, textvariable=self.budget_var).grid(
            row=3, column=0, sticky="ew", padx=8, pady=(4, 12))

        ttk.Label(form, text="Maximum Distance (km)").grid(
            row=2, column=1, sticky="w", padx=8)
        ttk.Entry(form, textvariable=self.distance_var).grid(
            row=3, column=1, sticky="ew", padx=8, pady=(4, 12))

        self.add_dropdown(form, "Minimum Rating", self.rating_var,
            ["Any", "3.5", "4.0", "4.5"], 4, 0)
        self.add_dropdown(form, "Dietary Requirement", self.dietary_var,
            ["Any", "Vegetarian", "Vegan", "Gluten-Free"], 4, 1)
        self.add_dropdown(form, "Sort Results By", self.sort_var,
            ["Distance", "Rating", "Price"], 6, 0)

        ttk.Button(form, text="Find Restaurants",
            command=self.find_restaurants).grid(
            row=7, column=1, sticky="ew", padx=8, pady=(4, 12))
        ttk.Button(form, text="Reset Filters",
            command=self.reset_filters).grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=8)

        self.summary = ttk.Label(
            self.root, text="Choose preferences and click Find Restaurants.",
            font=("Arial", 11, "bold"))
        self.summary.pack(anchor="w", padx=38, pady=(10, 5))

        self.output = tk.Text(self.root, wrap="word", height=15)
        self.output.pack(fill="both", expand=True, padx=38, pady=(0, 25))

# Read user input and search for matching restaurants
    def find_restaurants(self):
        try:
            budget = float(self.budget_var.get())
            max_distance = float(self.distance_var.get())
            if budget <= 0 or max_distance <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Budget and distance must be positive numbers.")
            return

        suburb = self.suburb_var.get().strip().lower()
        cuisine = self.cuisine_var.get().strip().lower()
        dietary = self.dietary_var.get().strip().lower()
        minimum_rating = (0 if self.rating_var.get() == "Any"
                          else float(self.rating_var.get()))

        matches = filter_restaurants(
            self.restaurants, cuisine, budget, suburb,
            max_distance, minimum_rating, dietary)
        matches = sort_restaurants(matches, self.sort_var.get())
        self.display_results(matches, budget, max_distance, minimum_rating)

# Display matching restaurants in the results area
    def display_results(self, matches, budget, max_distance, minimum_rating):
        self.output.delete("1.0", tk.END)

        if not matches:
            self.summary.config(text="No matching restaurants found.")
            self.output.insert(
                tk.END,
                "Try increasing your budget or distance, lowering the "
                "rating, or selecting Any.")
            return

        self.summary.config(
            text=f"{len(matches)} restaurant(s) found - "
                 f"sorted by {self.sort_var.get()}.")

        for number, restaurant in enumerate(matches, start=1):
            text = (
                f"{number}. {restaurant['name']}\n"
                f"   {restaurant['cuisine']} | "
                f"Rating: {restaurant['rating']:.1f}/5.0\n"
                f"   ${restaurant['average_price']:.0f} per person | "
                f"{restaurant['distance']:.2f} km away\n"
                f"   Suburb: {restaurant['suburb']} | "
                f"Dietary: {restaurant['dietary']}\n"
                f"   Why this matches: within ${budget:.0f} and "
                f"{max_distance:.1f} km")
            if minimum_rating > 0:
                text += f", rating {minimum_rating:.1f}+"
            text += "\n\n" + "-" * 55 + "\n\n"
            self.output.insert(tk.END, text)

# Reset all filters to their default values
    def reset_filters(self):
        self.suburb_var.set("Haymarket")
        self.cuisine_var.set("Any")
        self.budget_var.set("40")
        self.distance_var.set("3")
        self.rating_var.set("Any")
        self.dietary_var.set("Any")
        self.sort_var.set("Distance")
        self.summary.config(
            text="Choose preferences and click Find Restaurants.")
        self.output.delete("1.0", tk.END)

# Start the application
def main():
    root = tk.Tk()
    RestaurantFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
