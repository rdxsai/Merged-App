import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_collection("socratic_collection")
print("Documents:", collection.count())
