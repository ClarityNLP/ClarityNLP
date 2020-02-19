from pymongo import MongoClient
from flask import Response
import util

def writeResultFeedback(data):
    client = util.mongo_client()
    db = client[util.mongo_db]
    try:

        # Parsing info
        job_id = data['job_id']
        result_id = data['result_id']

        # checking if the results collection exists
        # if collection doesn't exist, creating
        collection = db['result_feedback']

        # checking if the result exists in Mongo
        query = {'result_id':result_id}
        existing_entry = collection.find_one(query)
        if existing_entry is None:
            # Writing a new result to Mongo
            collection.insert_one(data)
        else:
            # Updating existing result in Mongo
            updated_entry = data
            element = {"$set": updated_entry}
            collection.update_one(query, element)


        # returning 200 response
        return Response("Successfully wrote result feedback", status=200, mimetype='application/json')
    except Exception as e:
        # returning 400 response
        return Response(str(e), status=400, mimetype='application/json')
    finally:
        client.close()
