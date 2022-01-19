from flask import Flask, request, jsonify
from mysql import connector
import os
import logging



logging.basicConfig(filename="app.log",format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                      datefmt='%Y-%m-%d:%H:%M:%S',
                      level=logging.DEBUG)


app = Flask(__name__)

logging.info("Starting app")

password = os.environ['PASSWORD']

logging.info("Connecting to database")

try:
    # connect with mysql database
    mysql = connector.connect(user='root', password=password,
                              host='localhost', database='new_data')
    logging.info("Connected to database")
except Exception as e:
    logging.error("Error connecting to database")
    logging.error(e)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":

        # get json data from request
        json_data = request.json

        logging.info(json_data)
        name = json_data['name']
        username = json_data['username']
        # init cursor
        cur = mysql.cursor()

        # send data to mysql_server
        cur.execute(
            "INSERT INTO user (name, username) VALUES (%(name)s, %(username)s)", {"name":name, "username":username})

        # commit data and close the connection
        mysql.commit()
        cur.close()

        logging.info("Successully saved data")
        return jsonify({'message': f"name: {name} created succesfully!"})
    logging.info("Unsuccessful request")
    return jsonify({'message': 'Send post request'})


if __name__ == "__main__":
    app.run(debug=True)
