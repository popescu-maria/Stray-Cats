from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash, get_flashed_messages, make_response
from ..model.models import Cat, Nevoi
from ..extensions import db
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template("index.html")

@main.route('/add-cat', methods=['GET'])
def show_add_cat_form():
    nevoi_list = [n.name for n in Nevoi.query.all()]
    maps_api_key = current_app.config.get('Maps_API_KEY') or os.getenv('MAPS_API_KEY')
    # if not maps_api_key:
        # print("WARNING: Google Maps API key not found for adopt_care_map!")

    return render_template(
        "add_cat.html",
        nevoi_list=nevoi_list,
        maps_api_key=maps_api_key
    )
    # Maps_api_key = os.getenv('MAPS_API_KEY')
    # return render_template("add_cat.html", nevoi=nevoi_list, maps_api_key=Maps_api_key)

@main.route('/add-cat-form', methods=['POST'])
def handle_add_cat_form():
    nume = request.form.get('nume', '').strip()
    latitude_str = request.form.get('latitude')
    longitude_str = request.form.get('longitude')
    nevoi_names = request.form.getlist('nevoi')

    try:
        latitude = float(latitude_str)
        longitude = float(longitude_str)
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("Invalid coordinates.")
    except (ValueError, TypeError):
        return "Invalid latitude or longitude", 400

    try:
        new_cat = Cat(nume=nume, latitude=latitude_str, longitude=longitude_str)

        selected_nevoi = []
        for nevoi_name in nevoi_names:
            nevoi = Nevoi.query.filter_by(name=nevoi_name).first()
            if nevoi:
                selected_nevoi.append(nevoi)
            else:
                return f"Invalid nevoie: {nevoi_name}", 400

        new_cat.nevoi_list = selected_nevoi

        db.session.add(new_cat)
        db.session.commit()

        return redirect(url_for('main.home', status='cat_added_success'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

@main.route('/adopt-care', methods=['GET'])
def show_adopt_care_map():
    cats = Cat.query.all()
    cat_locations = []
    for cat in cats:
        try:
            lat = float(cat.latitude)
            lng = float(cat.longitude)
            cat_locations.append({'lat': lat, 'lng': lng})
        except (ValueError, TypeError):
            print(f"Warning: Invalid coordinates for cat {cat.id}: {cat.latitude}, {cat.longitude}")
            continue

    maps_api_key = current_app.config.get('Maps_API_KEY') or os.getenv('MAPS_API_KEY')
    if not maps_api_key:
        print("WARNING: Google Maps API key not found for adopt_care_map!")

    return render_template(
        "adopt_care.html",
        maps_api_key=maps_api_key,
        cat_locations=cat_locations
    )

@main.route('/cats/', methods=['GET'])
def get_cats():
    cats = Cat.query.all()
    return render_template("cats.html", cats=cats)

@main.route('/get-nevoi', methods=['GET'])
def get_nevoi():
    nevoi_list = [n.name for n in Nevoi.query.all()]
    return jsonify({"nevoi": nevoi_list})