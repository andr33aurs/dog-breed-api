from flask import Flask
from flask_restful import Api
from breed_group import BreedGroupList, BreedGroupItem
from breed import BreedItem, BreedList

app = Flask(__name__)
api = Api(app)

api.add_resource(BreedGroupList, "/breed-groups")
api.add_resource(BreedGroupItem, "/breed-groups/<string:id>")
api.add_resource(BreedItem, "/breeds/<string:id>")
api.add_resource(BreedList, "/breeds")

if __name__ == "__main__":
    app.run()


