from flask_restful import Resource, reqparse
from config import db_config
import mysql.connector


class BreedItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name")
    parser.add_argument("history")
    parser.add_argument("description")
    parser.add_argument("personality")
    parser.add_argument("grooming")
    parser.add_argument("living_conditions")
    parser.add_argument("training")
    parser.add_argument("usefulness")
    parser.add_argument("image")

    def fetch_breed(self, id, connection):
        """executes a SQL query to retrieve the breed with the specified ID,
        and returns the fetched breed as a dictionary."""
        breeds_cursor = connection.cursor(dictionary=True)
        breeds_cursor.execute("select * from breeds where id=%s", (id,))

        breed = breeds_cursor.fetchone()
        breeds_cursor.close()

        return breed

    def fetch_breed_with_characteristics(self, id, connection):
        """retrieve information about breed characteristics with the ID provided"""
        breed = self.fetch_breed(id, connection)

        if breed is None:
            return breed

        characteristics_cursor = connection.cursor(dictionary=True)
        characteristics_cursor.execute("select * from characteristics where breed_id=%s", (id,))

        characteristics = characteristics_cursor.fetchall()
        breed["characteristics"] = characteristics

        return breed

    def get(self, id):
        """fetches breed information along with their characteristics based on the breed ID"""
        connection = mysql.connector.connect(**db_config)

        breed = self.fetch_breed_with_characteristics(id, connection)

        if breed is None:
            return {"message": "Breed with id '{}' not found.".format(id)}, 404

        connection.close()

        return {"data": breed}, 200

    def patch(self, id):
        """fetches the breed based on the provided breed ID and
        executes the update query with the appropriate values."""

        connection = mysql.connector.connect(**db_config)
        breed = self.fetch_breed(id, connection)

        if breed is None:
            connection.close()
            return {"message": "Breed with id '{}' not found.".format(id)}, 404

        data = BreedItem.parser.parse_args()

        data_dict = {key: value for key, value in data.items() if value is not None}

        is_data_dict_empty = not bool(data_dict)

        if is_data_dict_empty:
            connection.close()
            return {"message": "At least one argument is required"}, 400

        set_clause = ", ".join([f"{key}=%s" for key in data_dict])
        update_query = f"update characteristics set {set_clause} where breed_id={id}"
        update_values = tuple(data_dict.values())

        update_breed_cursor = connection.cursor(dictionary=True)
        update_breed_cursor.execute(update_query, update_values)

        connection.commit()
        update_breed_cursor.close()

        breed = self.fetch_breed_with_characteristics(id, connection)
        connection.close()

        return {"data": breed}, 200

    def delete(self, id):
        """removes a breed and its associated characteristics from the database based on the given breed ID."""
        connection = mysql.connector.connect(**db_config)
        breed = self.fetch_breed(id, connection)

        if breed is None:
            connection.close()
            return {"message": "Breed with id '{}' not found.".format(id)}, 404

        characteristics_cursor = connection.cursor(dictionary=True)
        characteristics_cursor.execute("""
            delete from characteristics where breed_id=%s
        """, (id,))

        breed_cursor = connection.cursor(dictionary=True)
        breed_cursor.execute("""
            delete from breeds where id=%s
        """, (id,))

        connection.commit()
        characteristics_cursor.close()
        breed_cursor.close()

        connection.close()

        return "", 204


class BreedList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True, help="Property 'name' is required")
    parser.add_argument("history")
    parser.add_argument("description")
    parser.add_argument("personality")
    parser.add_argument("grooming")
    parser.add_argument("living_conditions")
    parser.add_argument("training")
    parser.add_argument("usefulness")
    parser.add_argument("image")
    parser.add_argument("breed_group_id", type=int, required=True, help="Property 'breed_group_id' is required")

    def post(self):
        data = BreedList.parser.parse_args()

        connection = mysql.connector.connect(**db_config)
        breeds_cursor = connection.cursor(dictionary=True)

        breeds_cursor.execute("""
            insert into breeds (name, breed_group_id)
            values (%s, %s)
        """, (data["name"], data["breed_group_id"]))

        breed_id = breeds_cursor.lastrowid

        characteristics_cursor = connection.cursor(dictionary=True)

        characteristics_cursor.execute("""
            insert into characteristics (history, description, personality, 
            grooming, living_conditions, training, usefulness, image, breed_id)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (data["history"], data["description"], data["personality"], data["grooming"],
              data["living_conditions"], data["training"],
              data["usefulness"], data["image"], breed_id))

        characteristics_id = characteristics_cursor.lastrowid

        connection.commit()
        breeds_cursor.close()
        characteristics_cursor.close()
        connection.close()

        characteristics = {key: value for key, value in data.items() if key not in ["name", "breed_group_id"]}
        characteristics["id"] = characteristics_id

        return {
            "data": {
                "id": breed_id,
                "name": data["name"],
                "characteristics": characteristics
            }
        }
