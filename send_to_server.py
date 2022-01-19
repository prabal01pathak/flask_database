import requests
import json
from mysql import connector
import os
import random
import logging

logging.basicConfig(level=logging.DEBUG,filename="send_to_server.log",
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

password = os.environ['PASSWORD']
mysql = connector.connect(user='root', password=password,
                          host='localhost', database='new_data')

# FAKE DATA
new_data = random.randint(1, 100)
data = {
    "name": "Jhonn",
    "username": str(new_data),
}


# it will send data to server and save it locally
def send_save_data(data):
    """
    send_save_data(data) takes data and save it locally 
    and send to other server 
    """
    cur = mysql.cursor()

    # status if failed or success to send other server
    status = False

    insert_query = "INSERT INTO backup_user (name, username,other_status) VALUES (%s, %s, %s)"

    # send data to other server using post method
    status_code = 404
    try:
        send_data = requests.post("http://localhost:5000/", json=data)
        status_code = send_data.status_code
    except Exception as e:
        logging.error(
            "error in sending data to other server", exec_info=True)
    finally:
        if status_code == 200:
            status = True
            cur.execute(insert_query, (data['name'], data['username'], status))
            mysql.commit()
            cur.close()

            # logging
            logging.info(
                f"name: {data['username']} created succesfully!  send to other server")
            return json.dumps({'message': f"name: {data['username']} created succesfully! send to other server"})
        else:
            cur.execute(insert_query, (data['name'], data['username'], status))
            mysql.commit()
            cur.close()
            logging.info(
                {'message': f"name: {data['username']} created succesfully! but not send to other server"})
            return json.dumps({'message': f"name: {data['username']} created succesfully! but not send to other server"})


def send_remain_data():
    """ 
    it will send data remaining data to other server 
    """
    cur = mysql.cursor()

    # get all data where status_code = false
    cur.execute("SELECT * FROM backup_user WHERE other_status = False")
    result = cur.fetchall()
    logging.info(f"fetch result:  {result}")

    # if rseult length > 0 then try to send them again.
    if len(result) > 0:
        logging.info("sending remaining data")
        for row in result:
            # form dataset
            data = {
                "name": row[0],
                "username": row[1]
            }

            # change if request status_code is ok.
            status_code = 404

            # try to send the data
            try:
                # send data to server
                send_data = requests.post("http://localhost:5000/", json=data)
                status_code = send_data.status_code

                # if data sent successfully then update it in local database
                logging.info("updating data")
                cur.execute(
                    "UPDATE backup_user SET other_status = True WHERE name= %s and username=%s AND other_status=False", (row[0], row[1]))

                mysql.commit()
                logging.info(f"{row[1]} successfully send to other server")
            except Exception as e:
                logging.error(
                    "Error in sending data to other server", exc_info=True)
            finally:
                if status_code != 200:
                    logging.info("Host is down")
                    return json.dumps({"message": "Host is down"})
        cur.close()
        return json.dumps({"message": "All data Sent to server"})
    cur.close()
    return json.dumps({"message": "no data available to send to server"})
print(send_save_data(data))
print(send_remain_data())
