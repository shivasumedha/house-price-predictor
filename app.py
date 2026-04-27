from flask import Flask, render_template, request
import math
import numpy as np
import pandas as pd

app = Flask(__name__)

# ---------------------------------
# Store History
# ---------------------------------
history = []

# Dashboard Counts
budget_count = 0
standard_count = 0
premium_count = 0

# ---------------------------------
# DataFrame for Analytics
# ---------------------------------
records = pd.DataFrame(
    columns=[
        "Area",
        "Bedrooms",
        "Bathrooms",
        "Location",
        "Parking",
        "Age",
        "Price"
    ]
)

# ---------------------------------
# Price Prediction Logic
# ---------------------------------
def calculate_price(area, bedrooms, bathrooms, location, parking, age):

    # NumPy calculation
    values = np.array([
        area * 5000,
        bedrooms * 300000,
        bathrooms * 200000
    ])

    price = np.sum(values)

    # Location Bonus
    if location == "Prime":
        price += 1500000
    elif location == "Standard":
        price += 700000
    else:
        price += 200000

    # Parking Bonus
    if parking == "Yes":
        price += 500000

    # Age Depreciation
    price -= age * 100000

    if price < 1000000:
        price = 1000000

    return round(price)

# ---------------------------------
# EMI Calculator
# ---------------------------------
def calculate_emi(price):
    loan = price * 0.80
    annual_rate = 8.5
    monthly_rate = annual_rate / 12 / 100
    months = 20 * 12

    emi = loan * monthly_rate * ((1 + monthly_rate) ** months)
    emi = emi / (((1 + monthly_rate) ** months) - 1)

    return round(emi)

# ---------------------------------
# Main Route
# ---------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    global budget_count, standard_count, premium_count, records

    estimated_price = ""
    category = ""
    emi = ""
    avg_price = ""

    if request.method == "POST":

        area = int(request.form["area"])
        bedrooms = int(request.form["bedrooms"])
        bathrooms = int(request.form["bathrooms"])
        location = request.form["location"]
        parking = request.form["parking"]
        age = int(request.form["age"])

        estimated_price = calculate_price(
            area, bedrooms, bathrooms,
            location, parking, age
        )

        emi = calculate_emi(estimated_price)

        # Category
        if estimated_price >= 10000000:
            category = "Premium Property 🏡"
            premium_count += 1

        elif estimated_price >= 5000000:
            category = "Standard Property 🏠"
            standard_count += 1

        else:
            category = "Budget Property 🏘️"
            budget_count += 1

        # History
        history.insert(
            0,
            f"{area} sqft | {bedrooms} BHK → ₹{estimated_price}"
        )

        if len(history) > 5:
            history.pop()

        # Save into Pandas DataFrame
        new_row = pd.DataFrame([{
            "Area": area,
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Location": location,
            "Parking": parking,
            "Age": age,
            "Price": estimated_price
        }])

        records = pd.concat([records, new_row], ignore_index=True)

        # Average Price Analytics
        avg_price = round(records["Price"].mean())

    return render_template(
        "index.html",
        estimated_price=estimated_price,
        category=category,
        emi=emi,
        history=history,
        budget=budget_count,
        standard=standard_count,
        premium=premium_count,
        avg_price=avg_price
    )

# ---------------------------------
# Run App
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)