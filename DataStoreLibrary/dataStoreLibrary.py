import json
import uuid
import boto3
from .helpers import standard_response
from dicttoxml import dicttoxml
from pathlib import Path
from django.conf import settings
from django.http import FileResponse


class DataStore:

    @staticmethod
    def __file_convert(data, form):
        if form.lower() == "json":
            return json.dumps(data, indent=2)
        if form.lower() == "xml":
            return dicttoxml(data).decode()
        if form.lower() == "byte":
            return json.dumps(data, indent=2).encode('utf-8')

    @staticmethod
    def __save_data_local(item, file_format):
        file_name = item['name']
        file_data = item['file']
        file_data = DataStore.__file_convert(file_data, file_format)
        write_method = "xb" if file_format == "byte" else "x"
        file_extension = "txt" if file_format == "byte" else file_format
        with open(f"DataStoreLibrary/files/{file_name}.{file_extension}", write_method) as file:
            file.write(file_data)

    @staticmethod
    def __save_data_s3(item, file_format):
        file_name = item['name']
        file_data = item['file']
        file_data = DataStore.__file_convert(file_data, file_format)
        s3 = DataStore.__connect_s3()
        file_key = f"files/{file_name}.{file_format}"
        try:
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Body=file_data,
                Key=file_key
            )
        except Exception as e:
            raise e

    @staticmethod
    def __update_data_local(item, file_format):
        file_name = item['name']
        file_data = item['file']
        file_data = DataStore.__file_convert(file_data, file_format)
        write_method = "wb" if file_format == "byte" else "w"
        file_extension = "txt" if file_format == "byte" else file_format
        file = Path(f"DataStoreLibrary/files/{file_name}.{file_extension}")
        if file.is_file():
            with open(f"DataStoreLibrary/files/{file_name}.{file_extension}", write_method) as file:
                file.write(file_data)
        else:
            raise Exception("The file does not exist!!!")

    @staticmethod
    def __update_data_s3(item, file_format):
        file_name = item['name']
        file_data = item['file']
        file_data = DataStore.__file_convert(file_data, file_format)
        s3 = DataStore.__connect_s3()
        file_key = f"files/{file_name}.{file_format}"
        try:
            file = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_key
            )
        except Exception:
            raise Exception("The file does not exist!!!")

        try:
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Body=file_data,
                Key=file_key
            )
        except Exception as e:
            raise e

    @staticmethod
    def record_insert(items, file_format='json', data_store='local'):
        response = standard_response.copy()
        response['result'] = []
        if isinstance(items, list):
            for item in items:
                item['name'] = item['name'] + "-" + str(uuid.uuid4())[:4]
                if data_store == 'local':
                    try:
                        DataStore.__save_data_local(item, file_format)
                    except Exception as e:
                        response['error'] = str(e)
                        return response
                elif data_store == 's3':
                    try:
                        DataStore.__save_data_s3(item, file_format)
                    except Exception as e:
                        response['error'] = str(e)
                        return response
                response['result'].append(f"file with id: '{item['name']}' has been uploaded successfully!!!!")
        else:
            raise Exception("Files should be in list!!!")
        response['is_success'] = True
        response['message'] = "Files uploaded successfully!!!"
        return response

    @staticmethod
    def record_update(file, file_format='json', data_source='local'):
        response = standard_response.copy()
        response['result'] = []
        if data_source == 'local':
            try:
                DataStore.__update_data_local(file, file_format)
            except Exception as e:
                if e == "The file does not exist!!!":
                    response['result'].append(str(e))
                else:
                    response['error'] = str(e)
                    response['result'] = None
                    return response
        elif data_source == 's3':
            try:
                DataStore.__update_data_s3(file, file_format)
            except Exception as e:
                if e == "The file does not exist!!!":
                    response['result'].append(str(e))
                else:
                    response['error'] = str(e)
                    response['result'] = None
                    return response
        response['result'].append(f"file with id: '{file['name']}' has been updated successfully!!!!")
        return response

    @staticmethod
    def record_delete(files, file_format='json', data_source='local'):
        response = standard_response.copy()
        response['error'] = []
        response['result'] = []
        for file_id in files:
            try:
                if data_source == 'local':
                    try:
                        DataStore.__delete_data_local(file_id, file_format)
                        response['result'].append(f"file with id: '{file_id}' has been deleted successfully!!!!")
                    except Exception as e:
                        if e == "The file does not exist!!!":
                            response['result'].append(str(e))
                        else:
                            response['error'] = str(e)
                            response['result'] = None
                elif data_source == 's3':
                    try:
                        DataStore.__delete_data_s3(file_id, file_format)
                        response['result'].append(f"file with id: '{file_id}' has been deleted successfully!!!!")
                    except Exception as e:
                        if e == "The file does not exist!!!":
                            response['result'].append(str(e))
                        else:
                            response['error'] = str(e)
                            response['result'] = None
                            return response
            except Exception as e:
                response['error'] = str(e)
                response['result'] = None
                return response
        response['is_success'] = True
        return response

    @staticmethod
    def __delete_data_local(file_id, file_format):
        file_extension = "txt" if file_format == "byte" else file_format
        file = Path(f"DataStoreLibrary/files/{file_id}.{file_extension}")
        if file.is_file():
            file.unlink()
        else:
            raise Exception("The file does not exist!!!")

    @staticmethod
    def __delete_data_s3(file_id, file_format):
        s3 = DataStore.__connect_s3()
        file_key = f"files/{file_id}.{file_format}"
        try:
            file = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_key
            )
        except Exception:
            raise Exception("The file does not exist!!!")

        try:
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_key
            )
        except Exception as e:
            raise e

    @staticmethod
    def __connect_s3():
        return boto3.client('s3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                            )

    @staticmethod
    def record_get(file_name, data_source='local', query=None, offset=None, limit=None):
        response = standard_response.copy()
        response['error'] = []
        response['result'] = []
        try:
            if data_source == 'local':
                try:
                    return DataStore.__get_data_local(file_name, query, offset, limit)
                except Exception as e:
                    if e == "The file does not exist!!!":
                        response['result'].append(str(e))
                    else:
                        response['error'] = str(e)
                        response['result'] = None
            elif data_source == 's3':
                try:
                    return DataStore.__get_data_s3(file_name, query, offset, limit)
                except Exception as e:
                    if e == "The file does not exist!!!":
                        response['result'].append(str(e))
                    else:
                        response['error'] = str(e)
                        response['result'] = None
                        return response
        except Exception as e:
            response['error'] = str(e)
            response['result'] = None
            return response

    @staticmethod
    def __get_data_local(file_name, query=None, offset=None, limit=None):
        if file_name:
            file_format = file_name.split(".")[1]
            file_id = file_name.split(".")[0]
            file_extension = "txt" if file_format == "byte" else file_format
            file = Path(f"DataStoreLibrary/files/{file_id}.{file_extension}")
            if file.is_file():
                return file.open()
            else:
                raise Exception("The file does not exist!!!")
        else:
            print("came here")
            try:
                offset = int(offset) if offset else 0
            except Exception as e:
                print("exc")
                raise Exception("for getting list from local offset should be an integer")
            print(offset)
            p = Path('.')
            list_files = list(p.glob(f'DataStoreLibrary/files/*{query}*.*'))
            if offset + limit <= len(list_files):
                list_files = list_files[offset:offset + limit]
                names = []
                for item in list_files:
                    names.append(item.name)
                print(names)
                result = {
                    "files": names,
                    "next": offset + limit
                }
            else:
                list_files = list_files[offset::]
                names = []
                for item in list_files:
                    names.append(item.name)
                print(names)
                result = {
                    "files": names
                }
            print(result)
            return result

    @staticmethod
    def __get_data_s3(file_name, query=None, offset=None, limit=None):
        s3 = DataStore.__connect_s3()
        if file_name:
            file_format = file_name.split(".")[1]
            file_id = file_name.split(".")[0]
            file_key = f"files/{file_id}.{file_format}"
            path = settings.AWS_CLOUD_FRONT_URL + f"files/{file_id}.{file_format}"
            try:
                file = s3.get_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=file_key
                )
            except Exception:
                raise Exception("The file does not exist!!!")
            data = {
                "file": file['Body'].read(),
                "path": path
            }
            return data
        else:
            if offset:
                s3_response = s3.list_objects_v2(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    MaxKeys=limit,
                    Prefix=f'files/{query}',
                    StartAfter=offset,
                    FetchOwner=False
                )
            else:
                s3_response = s3.list_objects_v2(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    MaxKeys=limit,
                    Prefix=f'files/{query}',
                    FetchOwner=False
                )
            file_list = list()
            for file in s3_response['Contents']:
                file_list.append(f"{settings.AWS_CLOUD_FRONT_URL}{file['Key']}")
            response = {
                "files": file_list,
            }
            if len(file_list) == limit:
                response['next'] = s3_response['Contents'][-1]['Key']
            return response
