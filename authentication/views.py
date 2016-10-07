from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.response import Response

from . import smscode, authtoken
from .serializers import PhoneSerializer, ConfirmPhoneSerializer

User = get_user_model()


@api_view(['POST'])
def send_code(request):
    serializer = PhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = serializer.validated_data['phone']
    try:
        smscode.new(phone)
    except smscode.LimitExceededError:
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
        smscode.validate(phone, code)
    except smscode.ValidationError:
        raise ValidationError({'code': 'Code is invalid.'})
    except smscode.LimitExceededError:
        raise Throttled()
    print(authtoken.get_or_create(1))
    return Response()
