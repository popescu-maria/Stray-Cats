from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

uri = "mongodb+srv://Poppy:123@cluster0.evldllk.mongodb.net/cats_database?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client['cats_database']
cats_collection = db['cats']


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/add-cat/', methods=['POST'])
def add_cat():
    cat_data = request.get_json()
    latitude = cat_data.get('latitude')
    longitude = cat_data.get('longitude')

    cat = {
        "latitude": latitude,
        "longitude": longitude
    }
    result = cats_collection.insert_one(cat)

    return jsonify({"message": "Cat added successfully!", "id": str(result.inserted_id)}), 201


@app.route('/cats/', methods=['GET'])
def get_cats():
    cats = list(cats_collection.find({}))
    for cat in cats:
        cat["_id"] = str(cat["_id"])
    return render_template("cats.html", cats=cats)


@app.route('/map')
def map_view():
    return render_template("map.html")


if __name__ == '__main__':
    app.run(debug=True)
