from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .dataStoreLibrary import *
import traceback
from django.http import FileResponse
# Create your views here.


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
def items(request):
    data_store = DataStore()
    if request.method == "GET":
        file_name = request.query_params.get('file_name', None)
        source = request.query_params.get('source', None)
        if not file_name:
            query = request.query_params.get('query', None)
            offset = request.query_params.get('offset', None)
            limit = request.query_params.get('limit', None)
            if limit:
                limit = int(limit)
            else:
                limit=10
        try:
            response = data_store.record_get(file_name, source, query, offset, limit)
        except :
            return Response(data=f"Error occurred", status=400)
        if not response:
            return Response(data="File does not exist!!!", status=300)
        return Response(data=response, status=200)
    if request.method == "POST":
        data = request.data
        try:
            result = data_store.record_insert(data['files'], data.get("type"), data.get('data_source'))
        except Exception as e:
            return Response(data=f"Error occurred {str(e)}", status=400)

        return Response(data=result, status=200)

    if request.method == "PATCH":
        data = request.data
        try:
            result = data_store.record_update(data['file'], data['type'], data['data_source'])
        except Exception as e:
            return Response(data=f"Error occurred {str(e)}", status=400)

        return Response(data=result, status=200)

    if request.method == "DELETE":
        data = request.data
        try:
            result = data_store.record_delete(data['file_ids'], data['type'], data['data_source'])
        except Exception as e:
            return Response(data=f"Error occurred {str(e)}", status=400)

        return Response(data=result, status=200)



