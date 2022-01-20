import requests
import json
import os
import random
import logging
import asyncio
import aiomysql

#logging.basicConfig(level=logging.DEBUG,filename="send_to_server.log",
#                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

logging.basicConfig(filename="send_to_server.log",format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.DEBUG)


async def connect_to_database():
    """
    connect to database
    """
    password = os.environ['PASSWORD']
    try:
        mysql = await aiomysql.connect(
            host='localhost',
            user='root',
            password=password,
            db='new_data'
        )
        return mysql
    except Exception as e:
        logging.error(
            "Error in connecting to database", exc_info=True)
        return None


# FAKE DATA
new_data = random.randint(1, 100)
data = {
    "name": "prabal",
    "username": str(new_data)+"prabal",
}


async def send_save_data(data):
    """
    send_save_data(data) takes data and save it locally 
    and send to other server 
    """

    # status if failed or success to send other server
    status = False

    insert_query = "INSERT INTO backup_user (name, username,other_status) VALUES (%(name)s, %(username)s, %(status)s)"

    # send data to other server 
    #status_code = 404
    mysql = await asyncio.create_task(connect_to_database())
    cur =  await mysql.cursor()
    await cur.execute(insert_query, {"name":data['name'], "username":data['username'],"status":status})
    await mysql.commit()
    await cur.close()
    mysql.close()
    logging.info(
        {'message': f"name: {data['username']} created succesfully! but not send to other server"})
    return json.dumps({'message': f"name: {data['username']} created succesfully! but not send to other server"})


async def send_remain_data():
    """ 
    it will send data remaining data to other server 
    """
    mysql = await asyncio.create_task(connect_to_database())
    cur =await mysql.cursor()

    # get all data where status_code = false
    await cur.execute("SELECT * FROM backup_user WHERE other_status = False")
    result = await cur.fetchall()
    logging.info(f"Fetch result:  {result}")

    # if rseult length > 0 then try to send them again.
    if len(result) > 0:
        logging.info("Sending remaining data")
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
                send_data = requests.post("http://localhost:5000/", json=data, timeout=0.5)
                print(send_data.status_code)
                status_code = send_data.status_code

            except Exception as e:
                logging.error(
                    "Error in sending data to other server", exc_info=True)

            finally:
                # if data sent successfully then update it in local database
                if status_code == 200:
                    logging.info("Updating data")
                    await cur.execute(
                            "UPDATE backup_user SET other_status = True WHERE name= %(name)s and username=%(username)s AND other_status=False", {"name":row[0], "username":row[1]})

                    await mysql.commit()
                    logging.info(f"{row[1]} Successfully send to other server")
                else:
                    logging.info("Host is down")
                    logging.info(f"Status Code: {status_code}")
                    await cur.close()
                    mysql.close()
                    return json.dumps({"message": "Host is down"})
        await cur.close()
        mysql.close()
        return json.dumps({"message": "All data Sent to server"})

    await cur.close()
    mysql.close()
    return json.dumps({"message": "No data available for send to the server"})

async def main(data):
    """
    main function
    """
    l = await asyncio.gather(send_save_data(data))
    m = await asyncio.gather(send_remain_data())
    print(l)
    print(m)

if __name__ == "__main__":
    asyncio.run(main(data))

