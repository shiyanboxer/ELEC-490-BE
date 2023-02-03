# import pymongo 
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

# def connect_db():
#     try:
#         # Make a Connection with MongoClient. Create a MongoClient to the running mongod instance.
#         # https://stackoverflow.com/questions/54484890/ssl-handshake-issue-with-pymongo-on-python3
#         CONNECTION_STRING = 'mongodb+srv://elec49x:' + MONGO_PASSWORD + '@cluster0.eqv2bql.mongodb.net/test'
#         client = pymongo.MongoClient(CONNECTION_STRING, tlsAllowInvalidCertificates=True)
#         # Get collection
#         db = client['users']
#         collection = db['data']

#     # If connecting to the database fails, then return an error message and set isError = True
#     except Exception as e:
#         return 'Unable to connect to database'
#     return collection
