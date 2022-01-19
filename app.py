from flask import Flask, request, jsonify
from mysql import connector
import os


app = Flask(__name__)

password = os.environ['PASSWORD']
# connect with mysql database
mysql = connector.connect(user='root', password=password,
                          host='localhost', database='new_data')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        print("post method ")
        # get json data from request
        json_data = request.json
        print(json_data)
        name = json_data['name']
        username = json_data['username']
        # init cursor
        cur = mysql.cursor()

        # send data to mysql_server
        cur.execute(
            "INSERT INTO user (name, username) VALUES (%s, %s)", (name, username))

        # commit data and close the connection
        mysql.commit()
        cur.close()
        print("success")
        return jsonify({'message': f"name: {name} created succesfully!"})
    print("unsuccess")
    return jsonify({'message': 'send post request'})


if __name__ == "__main__":
    app.run(debug=True)
