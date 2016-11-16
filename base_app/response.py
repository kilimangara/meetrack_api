from rest_framework.response import Response


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


def ErrorResponse(error_type, status, serializer_errors=None, description=None, **kwargs):
    if description is None and serializer_errors is not None:
        description = errors_to_description(serializer_errors)
    description = description or error_type
    data = {
        'error': {
            'type': error_type,
            'status_code': status,
            'description': description
        }
    }
    return Response(data, status, **kwargs)
