# Y42-task
Technical task for Y42


Stack task:

in file stackGenerator.py I have implemented the stack class you can work with
It supports all the functions required
- Tests are ready and you can run them with django tests

Data store Library:

Data store support:
- local
- s3
Format Support:
- json
- xml
- byte

Functionality supports:
● Record inserts & batch inserts
● Record query/retrieval
● Query filters , limit & offset
● Update and delete operations

endpoint for it is just  http://127.0.0.1:8000/upload/
with methods you can get various functionalites

GET :
You can get one object if you only use (file_name, source) query params to get specific object
example: http://127.0.0.1:8000/upload/?file_name=sohrab-1ddf.xml&source=local&limit=5
You can get a query with (source, query, offset, limit)
example: http://127.0.0.1:8000/upload/?source=local&query=nasim&offset=25&limit=5

POST: 
To insert a file

body: {
    "type": "str", # xml or json or byte
    "data_source": "str", # local or s3
    "files":[
        {
            "name": "str",
            "file":"dict"
        }
    ]
}


DELETE: 
To delete file(s)

{
    "type": "str", # xml or json or byte
    "data_source":  "str", # local or s3
    "file_ids": ["str"], # list of files full name e.g(sohrab-a7c3)
}

PATCH
To update a file 

{
    "type": "str", # xml or json or byte
    "data_source": "str", # local or s3
    "file":
        {
            "name": "str", # file full name e.g(sohrab-a7c3)
            "file": "dict"
        }
}
