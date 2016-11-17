from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ValidationError, ParseError
from .error_types import INVALID_REQUEST_DATA, INVALID_AUTH_TOKEN


def SuccessResponse(data=None, status=None, **kwargs):
    data = data or {}
    return Response({'data': data}, status, **kwargs)


def errors_to_description(serializer_errors):
    errors_list = []
    for field, field_errors in serializer_errors.items():
        if not field_errors:
            continue
        errors_list.append('{}: {}'.format(field, field_errors[0]))
    description = ' '.join(errors_list)
    return description


def error_response_content(error_type, status_code, description):
    return {
        'error': {
            'status_code': status_code,
            'type': error_type,
            'description': description,
        }
    }


def ErrorResponse(error_type, status, serializer_errors=None, description=None, **kwargs):
    if description is None and serializer_errors is not None:
        description = errors_to_description(serializer_errors)
    description = description or error_type
    return Response(error_response_content(error_type, status, description), status, **kwargs)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = error_response_content(INVALID_AUTH_TOKEN, exc.status_code, exc.detail)
        if isinstance(exc, (ValidationError, ParseError)):
            response.data = error_response_content(INVALID_REQUEST_DATA, exc.status_code, exc.detail)
    return response
