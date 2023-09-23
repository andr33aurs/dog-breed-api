from flask_restful import Resource
from config import db_config
import mysql.connector


class BreedGroupList(Resource):
    """returns the breed groups from mySQL database(dog-breeds)"""

    def get(self):
        connection = mysql.connector.connect(**db_config)

        cursor = connection.cursor(dictionary=True)
        cursor.execute("select * from breed_groups")

        breed_groups = cursor.fetchall()

        cursor.close()
        connection.close()

        return {"data": breed_groups}, 200


class BreedGroupItem(Resource):
    """returns the breeds from the selected breed group"""

    def get(self, id):
        connection = mysql.connector.connect(**db_config)

        breed_groups_cursor = connection.cursor(dictionary=True)
        breed_groups_cursor.execute("select * from breed_groups where id=%s", (id,))

        breed_group = breed_groups_cursor.fetchone()

        breed_groups_cursor.close()

        if breed_group is None:
            connection.close()
            return {"message": "Breed group with id '{}' not found.".format(id)}, 404

        breeds_cursor = connection.cursor(dictionary=True)
        breeds_cursor.execute("select * from breeds where breed_group_id=%s", (id,))

        breeds = breeds_cursor.fetchall()
        breed_group["breeds"] = breeds

        connection.close()

        return {"data": breed_group}, 200




