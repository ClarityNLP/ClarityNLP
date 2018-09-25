from pymongo import MongoClient
from flask import Response

def writeResultFeedback(host, port, database, data):
    try:
        # connecting to the Mongo DB
        client = MongoClient(host, port)
        db = client[database]

        # checking if the results collection exists
        # if collection doesn't exist, creating
        if 'result_feedback' not in db.list_collection_names():
            collection = db['result_feedback']

        # Writing the result to Mongo
        entry_id = collection.insert_one(data).inserted_id



        # returning 200 response
        return Response("Successfully wrote result feedback", status=200, mimetype='application/json')
    except Exception as e:
        # returning 400 response
        return Response(str(e), status=400, mimetype='application/json')
