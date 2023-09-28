from flask_restful import Resource, reqparse
from config import db_config
import mysql.connector


class BreedGroupList(Resource):
    """returns the breed group list from mySQL database(dog-breeds) in JSON format"""

    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True, help="Property 'name' is required!")

    def get(self):
        """Establish a connection to the PlanetScale MySQL database,
        create a cursor to execute MySQL queries,
        fetch the results
        """
        connection = mysql.connector.connect(**db_config)

        cursor = connection.cursor(dictionary=True)
        cursor.execute("select * from breed_groups")

        breed_groups = cursor.fetchall()

        cursor.close()
        connection.close()

        return {"data": breed_groups}, 200

    def post(self):
        """Parse the data and execute a query to add a new breed group"""
        connection = mysql.connector.connect(**db_config)

        cursor = connection.cursor(dictionary=True)

        data = BreedGroupList.parser.parse_args()
        cursor.execute("insert into breed_groups (name) values (%s)", (data["name"],))

        breed_group_id = cursor.lastrowid

        connection.commit()
        cursor.close()
        connection.close()

        return {"data": {
            "id": breed_group_id,
            "name": data["name"]
        }}, 201


class BreedGroupItem(Resource):
    """returns the breed list from the selected breed group"""

    def get(self, id):
        connection = mysql.connector.connect(**db_config)

        breed_groups_cursor = connection.cursor(dictionary=True)
        breed_groups_cursor.execute("select * from breed_groups where id=%s", (id,))

        breed_group = breed_groups_cursor.fetchone()

        breed_groups_cursor.close()

        if breed_group is None:
            connection.close()
            return {"message": f"Breed group with id '{id}' not found."}, 404

        breeds_cursor = connection.cursor(dictionary=True)
        breeds_cursor.execute("select * from breeds where breed_group_id=%s", (id,))

        breeds = breeds_cursor.fetchall()
        breed_group["breeds"] = breeds

        connection.close()

        return {"data": breed_group}, 200
