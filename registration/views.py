import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from base_app.response import SuccessResponse, ErrorResponse
from .phone_storage import PhoneStorage

from authtoken import tokens
from .serializers import PhoneSerializer, ConfirmPhoneSerializer, NewUserSerializer, CodeSerializer

User = get_user_model()
INVALID_PHONE_NUMBER = 'INVALID_PHONE_NUMBER'
INVALID_PHONE_CODE = 'INVALID_PHONE_CODE'
PHONE_CODE_EXPIRED = 'PHONE_CODE_EXPIRED'
USER_NOT_FOUND = 'USER_NOT_FOUND'
CONFIRM_ATTEMPTS_EXCEEDED = 'CONFIRM_ATTEMPTS_EXCEEDED'
USER_ALREADY_EXISTS = 'USER_ALREADY_EXISTS'
INVALID_AUTH_TOKEN = 'INVALID_AUTH_TOKEN'
MEETING_NOT_FOUND = 'MEETING_NOT_FOUND'
YOU_NOT_KING = 'YOU_NOT_KING'
INVALID_REQUEST_DATA = 'INVALID_REQUEST_DATA'


class SMSSendingError(Exception):
    pass


def send_sms_code(phone, code):
    r = requests.post(settings.SMS_AUTH['REQUEST_URL'],
                      data={'To': phone, 'From': settings.SMS_AUTH['FROM_NUMBER'], 'Body': code},
                      auth=(settings.SMS_AUTH['ACCOUNT_SID'], settings.SMS_AUTH['AUTH_TOKEN']))
    if r.status_code != 201:
        raise SMSSendingError("Service response has incorrect status code", r)


@api_view(['POST'])
def send_code(request):
    phone_serializer = PhoneSerializer(data=request.data)
    if not phone_serializer.is_valid():
        return ErrorResponse(INVALID_PHONE_NUMBER, status.HTTP_400_BAD_REQUEST, phone_serializer.errors)
    phone_number = phone_serializer.validated_data['phone']
    phone_storage = PhoneStorage(phone_number)
    code = CodeSerializer.generate_code()
    phone_storage.set_code(code, lifetime=settings.SMS_AUTH['CODE_LIFE_TIME'])
    if not hasattr(settings, 'TEST_SMS'):
        send_sms_code(phone_number, code)
    is_new = not User.objects.filter(phone=phone_number).exists()
    return SuccessResponse({'is_new': is_new}, status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    phone_serializer = PhoneSerializer(data=request.data)
    if not phone_serializer.is_valid():
        return ErrorResponse(INVALID_PHONE_NUMBER, status.HTTP_400_BAD_REQUEST, phone_serializer.errors)
    code_serializer = CodeSerializer(data=request.data)
    if not code_serializer.is_valid():
        return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST, phone_serializer.errors)
    phone_number = phone_serializer.validated_data['phone']
    code = code_serializer.validated_data['code']
    phone_storage = PhoneStorage(phone_number)
    if not settings.DEBUG or code != settings.SMS_AUTH['DEBUG_CODE']:
        try:
            real_code = phone_storage.get_code()
        except PhoneStorage.DoesNotExist:
            return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST)
        count = phone_storage.get_attempts()
        if count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            return ErrorResponse(CONFIRM_ATTEMPTS_EXCEEDED, status.HTTP_429_TOO_MANY_REQUESTS)
        if code != real_code:
            phone_storage.increment_attempts(lifetime=settings.SMS_AUTH['ATTEMPTS_LIFE_TIME'])
            return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST)

    if not phone_confirm_serializer.validated_data['is_new']:
        try:
            user_id = User.objects.only('id').get(phone=phone_number).id
        except User.DoesNotExist:
            # save same code without lifetime
            phone_storage.set_code(code)
            return ErrorResponse(USER_NOT_FOUND,status.HTTP_404_NOT_FOUND)
    else:
        user_serializer = NewUserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return ErrorResponse(INVALID_REQUEST_DATA,user_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_id = user_serializer.save().id
    token = tokens.create(user_id)
    phone_confirm_serializer.deactivate_code()
    return Response({'token': token, 'user_id': user_id}, status.HTTP_201_CREATED)
