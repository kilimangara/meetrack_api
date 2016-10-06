from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.response import Response

from . import authcode
from .serializers import PhoneSerializer, ConfirmPhoneSerializer

User = get_user_model()


@api_view(['POST'])
def send_code(request):
    serializer = PhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = serializer.validated_data['phone']
    try:
        authcode.new(phone)
    except authcode.LimitExceededError:
        raise Throttled()
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    serializer = ConfirmPhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = serializer.validated_data['phone']
    code = serializer.validated_data['code']
    try:
        authcode.validate(phone, code)
    except authcode.ValidationError:
        raise ValidationError({'code': 'Code is invalid.'})
    except authcode.LimitExceededError:
        raise Throttled()
    return Response()
