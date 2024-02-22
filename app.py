from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from haversine import haversine

app = Flask(__name__)

def calculate_charge(start_location, end_location, vehicle_type):
    # Retrieve coordinates for start and end locations using geopy
    geolocator = Nominatim(user_agent="charge_calculator")
    start_coords = geolocator.geocode(start_location)
    end_coords = geolocator.geocode(end_location)

    # Calculate the distance between start and end locations using haversine
    distance = haversine((start_coords.latitude, start_coords.longitude),
                         (end_coords.latitude, end_coords.longitude), unit='km')

    # Rates for different vehicles
    rates = {
        'auto': {'first_km': 100.00, 'per_km': 50.00},
        'car': {'first_km': 200.00, 'per_km': 150.00},
        'van': {'first_km': 500.00, 'per_km': 350.00},
        'kdh': {'first_km': 1000.00, 'per_km': 850.00}
    }

    # Calculate the charge based on the given vehicle type
    rate_info = rates.get(vehicle_type.lower())
    if rate_info:
        first_km_charge = rate_info['first_km']
        per_km_charge = rate_info['per_km']
        
        if distance > 10:
            per_km_charge = 1 * per_km_charge

        total_charge = first_km_charge + (distance - 1) * per_km_charge
        distance = round(distance, 2)
        total_charge = round(total_charge, 2)
        return distance, total_charge
    else:
        return None, None

@app.route('/')
def index():
    return render_template('charge_calculator.html')

@app.route('/calculate_charge', methods=['POST'])
def calculate_charge_route():
    try:
        start_location = request.form['start_location']
        end_location = request.form['end_location']
        vehicle_type = request.form['vehicle_type'].lower()

        distance, charge = calculate_charge(start_location, end_location, vehicle_type)

        if distance is not None and charge is not None:
            return render_template('charge_result.html', start_location=start_location,
                                   end_location=end_location, vehicle_type=vehicle_type, distance=distance, charge=charge)
        else:
            return "Invalid vehicle type or locations."
    except ValueError:
        return "Invalid input. Please check your entries."

if __name__ == '__main__':
    app.run(debug=True)
