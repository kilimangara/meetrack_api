from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


def SuccessResponse(data=None, status=None, **kwargs):
    status = status or HTTP_200_OK
    data = data or {}
    return Response({'status_code': status, 'data': data}, status, **kwargs)


def ErrorResponse(error, status=None, fields=None, **kwargs):
    status = status or HTTP_400_BAD_REQUEST
    data = {'status_code': status, 'error': error}
    if fields is not None:
        data['fields'] = fields
    return Response(data, status, **kwargs)
