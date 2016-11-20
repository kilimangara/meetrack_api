import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view

from authtoken import tokens
from base_app.error_types import INVALID_PHONE_NUMBER, INVALID_PHONE_CODE, CONFIRM_ATTEMPTS_EXCEEDED
from base_app.error_types import USER_NOT_FOUND, USER_ALREADY_EXISTS
from base_app.response import SuccessResponse, ErrorResponse
from .phone_storage import PhoneStorage
from .serializers import PhoneSerializer, NewUserSerializer, CodeSerializer, IsNewUserSerializer

User = get_user_model()


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
        return ErrorResponse(INVALID_PHONE_NUMBER, status.HTTP_400_BAD_REQUEST, phone_serializer.errors_as_text)
    phone_number = phone_serializer.validated_data['phone']
    phone_storage = PhoneStorage(phone_number)
    code = CodeSerializer.generate_code()
    phone_storage.set_code(code, lifetime=settings.SMS_AUTH['CODE_LIFETIME'])
    if not hasattr(settings, 'TEST_SMS'):
        send_sms_code(phone_number, code)
    is_new = not User.objects.filter(phone=phone_number).exists()
    return SuccessResponse({'is_new': is_new}, status.HTTP_201_CREATED)


def is_sign_up(request):
    serializer = IsNewUserSerializer(data=request.data)
    if not serializer.is_valid():
        return False
    return serializer.validated_data['is_new']


@api_view(['POST'])
def login(request):
    phone_serializer = PhoneSerializer(data=request.data)
    phone_serializer.is_valid(raise_exception=True)
    code_serializer = CodeSerializer(data=request.data)
    if not code_serializer.is_valid():
        return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST, code_serializer.errors_as_text)
    phone_number = phone_serializer.validated_data['phone']
    code = code_serializer.validated_data['code']
    phone_storage = PhoneStorage(phone_number)
    if not settings.DEBUG or code != settings.SMS_AUTH['DEBUG_CODE']:
        try:
            real_code = phone_storage.get_code()
        except PhoneStorage.DoesNotExist:
            return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST, "Code does not exist or has expired.")
        attempts_count, wait_time = phone_storage.get_attempts()
        if attempts_count >= settings.SMS_AUTH['ATTEMPTS_LIMIT']:
            return ErrorResponse(CONFIRM_ATTEMPTS_EXCEEDED, status.HTTP_429_TOO_MANY_REQUESTS,
                                 "Try again later after {} seconds.".format(wait_time))
        if code != real_code:
            if attempts_count == 0:
                phone_storage.set_attempts(1, settings.SMS_AUTH['ATTEMPTS_LIFETIME'])
            else:
                phone_storage.increment_attempts()
            return ErrorResponse(INVALID_PHONE_CODE, status.HTTP_400_BAD_REQUEST, "The input code does not match.")
    if not is_sign_up(request):
        try:
            user_id = User.objects.only('id').get(phone=phone_number).id
        except User.DoesNotExist:
            # save same code without lifetime
            phone_storage.set_code(code)
            return ErrorResponse(USER_NOT_FOUND, status.HTTP_404_NOT_FOUND,
                                 "User with such phone number does not registered.")
    else:
        user_serializer = NewUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        if User.objects.filter(phone=phone_number).exists():
            return ErrorResponse(USER_ALREADY_EXISTS, status.HTTP_409_CONFLICT,
                                 "User with such phone number already registered in the system.")
        user_id = user_serializer.save().id
    token = tokens.create(user_id)
    phone_storage.delete_code()
    return SuccessResponse({'token': token, 'user': user_id}, status.HTTP_201_CREATED)
