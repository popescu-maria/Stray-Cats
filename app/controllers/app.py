from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
from ..Model.models import Cat, Nevoi, MetNeed
from ..Model.users import User
from ..extensions import db
import os
import requests
from flask_login import login_user, logout_user, current_user

main = Blueprint('main', __name__)

GOOGLE_GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def get_address_from_coords(latitude, longitude, api_key):
    if not api_key:
        print("Geocoding API key is missing.")
        return "Adresă indisponibilă (cheie API lipsă)"
    params = {
        "latlng": f"{latitude},{longitude}",
        "key": api_key,
        "language": "ro"
    }
    try:
        response = requests.get(GOOGLE_GEOCODING_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            return data['results'][0]['formatted_address']
        elif data['status'] == 'ZERO_RESULTS':
            return "Adresa nu a putut fi găsită pentru aceste coordonate."
        else:
            print(f"Geocoding API error: {data.get('error_message', data['status'])}")
            return "Eroare la interogarea API-ului de geocodare."
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed during geocoding: {e}")
        return "Eroare de rețea la găsirea adresei."
    except Exception as e:
        print(f"An unexpected error occurred during geocoding: {e}")
        return "Eroare necunoscută la găsirea adresei."

@main.route('/')
def home():
    return render_template("index.html")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists.'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered.'}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        try:
            db.session.commit()
            login_user(new_user)
            next_page = request.args.get('next')
            return jsonify({'success': True, 'message': 'Account created successfully! You are now logged in.', 'redirect': next_page or url_for('main.home')}), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error registering user {username}: {str(e)}")
            return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500
    else:
        flash("Please use the 'Create Account' button on the home page.", "info")
        return redirect(url_for('main.home', next=request.args.get('next')))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username_email = data.get('username_email')
        password = data.get('password')

        if not username_email or not password:
            return jsonify({'success': False, 'message': 'Username/Email and password are required.'}), 400

        user = User.query.filter((User.username == username_email) | (User.email == username_email)).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return jsonify({'success': True, 'message': 'Logged in successfully!', 'redirect': next_page or url_for('main.home')}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username/email or password.'}), 401
    else:
        flash("Please log in to access this page.", "info")
        return redirect(url_for('main.home', next=request.args.get('next')))

@main.route('/logout')
# @login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/add-cat', methods=['GET'])
def show_add_cat_form():
    nevoi_list = [n.name for n in Nevoi.query.all()]
    maps_api_key = current_app.config.get('MAPS_API_KEY') or os.getenv('MAPS_API_KEY')
    return render_template(
        "add_cat.html",
        nevoi_list=nevoi_list,
        maps_api_key=maps_api_key
    )

@main.route('/add-cat-form', methods=['POST'])
def handle_add_cat_form():
    nume = request.form.get('nume', '').strip()
    latitude_str = request.form.get('latitude')
    longitude_str = request.form.get('longitude')
    nevoi_names = request.form.getlist('nevoi')

    if not nume:
        return "Numele este obligatoriu.", 400

    try:
        latitude = float(latitude_str)
        longitude = float(longitude_str)
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Coordonate invalide.")
    except (ValueError, TypeError):
        return "Latitudine sau longitudine invalidă.", 400

    try:
        new_cat = Cat(nume=nume, latitude=latitude_str, longitude=longitude_str)

        selected_nevoi = []
        if nevoi_names:
            for nevoi_name in nevoi_names:
                nevoi = Nevoi.query.filter_by(name=nevoi_name).first()
                if nevoi:
                    selected_nevoi.append(nevoi)
                else:
                    print(f"Warning: Nevoie '{nevoi_name}' not found in database.")
        new_cat.nevoi_list = selected_nevoi

        db.session.add(new_cat)
        db.session.commit()

        flash('Pisică adăugată cu succes!', 'info')
        return redirect(url_for('main.home', status='cat_added_success'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding cat: {str(e)}")
        return f"Eroare la adăugarea pisicii: {str(e)}", 500

@main.route('/adopt-care', methods=['GET'])
def show_adopt_care_map():
    cats = Cat.query.all()
    cat_locations = []
    maps_api_key = current_app.config.get('MAPS_API_KEY') or os.getenv('MAPS_API_KEY')

    if not maps_api_key:
        print("AVERTISMENT: Cheia API Google Maps nu a fost găsită pentru harta adopt_care!")

    for cat in cats:
        try:
            lat = float(cat.latitude)
            lng = float(cat.longitude)
            address = "Adresă neprecizată"
            if maps_api_key:
                 address = get_address_from_coords(lat, lng, maps_api_key)

            nevoi_data_for_frontend = []
            for nevoi_item in cat.nevoi_list:
                if hasattr(nevoi_item, 'id') and hasattr(nevoi_item, 'name'):
                    is_met_recently = MetNeed.was_met_recently(cat.id, nevoi_item.id)
                    nevoi_data_for_frontend.append({
                        'id': nevoi_item.id,
                        'name': nevoi_item.name,
                        'is_met_recently': is_met_recently
                    })
                else:
                    print(f"Warning: Skipping malformed nevoi_item for cat {cat.nume} (ID: {cat.id}): {nevoi_item}")


            cat_locations.append({
                'id': cat.id,
                'lat': lat,
                'lng': lng,
                'nume': cat.nume,
                'nevoi': nevoi_data_for_frontend,
                'address': address
            })
        except (ValueError, TypeError) as e:
            print(f"Atenție: Coordonate invalide pentru pisica {cat.id}: {cat.latitude}, {cat.longitude}. Eroare: {e}")
            cat_locations.append({
                'id': cat.id,
                'lat': None,
                'lng': None,
                'nume': cat.nume,
                'nevoi': [],
                'address': "Coordonate invalide"
            })
            continue

    return render_template(
        "adopt_care.html",
        maps_api_key=maps_api_key,
        cat_locations=cat_locations,
        current_user_authenticated=current_user.is_authenticated
    )

@main.route('/check-need', methods=['POST'])
def check_need():
    data = request.get_json()
    cat_id = data.get('cat_id')
    nevoi_id = data.get('nevoi_id')

    if not all([cat_id, nevoi_id]):
        return jsonify({'success': False, 'message': 'Missing cat_id or nevoi_id'}), 400

    cat = Cat.query.get(cat_id)
    nevoi = Nevoi.query.get(nevoi_id)

    if not cat or not nevoi:
        return jsonify({'success': False, 'message': 'Cat or Nevoi not found'}), 404

    if MetNeed.was_met_recently(cat_id, nevoi_id):
        return jsonify({'success': True, 'message': 'Need already met recently.', 'is_met_recently': True}), 200

    try:
        new_met_need = MetNeed(cat_id=cat_id, nevoi_id=nevoi_id)
        db.session.add(new_met_need)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Need marked as met!', 'is_met_recently': True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking need as met for cat {cat_id}, nevoi {nevoi_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@main.route('/cats/', methods=['GET'])
def get_cats():
    if current_user.is_authenticated:
        cats_from_db = Cat.query.filter_by(user_id=current_user.id).all()
        flash(f"Showing cats added by {current_user.username}", 'info')
    else:
        cats_from_db = Cat.query.all()
        flash("Showing all cats (login to see only your own)", 'info')

    cats_with_addresses = []
    maps_api_key = current_app.config.get('MAPS_API_KEY') or os.getenv('MAPS_API_KEY')

    if not maps_api_key:
        print("AVERTISMENT: Cheia API Google Maps nu a fost găsită pentru lista de pisici!")

    for cat in cats_from_db:
        address = "Adresă neprecizată"
        try:
            lat = float(cat.latitude)
            lng = float(cat.longitude)
            if maps_api_key:
                address = get_address_from_coords(lat, lng, maps_api_key)
        except (ValueError, TypeError) as e:
            print(f"Atenție: Coordonate invalide pentru pisica {cat.id} în lista /cats/. Eroare: {e}")
            address = "Coordonate invalide"

        cats_with_addresses.append({
            'id': cat.id,
            'nume': cat.nume,
            'latitude': cat.latitude,
            'longitude': cat.longitude,
            'adresa': address,
            'nevoi_list': [n.name for n in cat.nevoi_list]
        })
    return render_template("cats.html", cats=cats_with_addresses)

@main.route('/get-nevoi', methods=['GET'])
def get_nevoi():
    nevoi_list = [n.name for n in Nevoi.query.all()]
    return jsonify({"nevoi": nevoi_list})