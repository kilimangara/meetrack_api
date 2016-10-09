from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from . import token_storage
from .serializers import SendPhoneSerializer, ConfirmPhoneSerializer, NewUserSerializer

User = get_user_model()


@api_view(['POST'])
def send_code(request):
    serializer = SendPhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save_code()
    if not hasattr(settings, 'TEST_SMS'):
        serializer.send_code()
    phone = serializer.validated_data['phone']
    is_new = not User.objects.filter(phone=phone).exists()
    return Response({'is_new': is_new}, status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    serializer = ConfirmPhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = serializer.validated_data['phone']
    if not serializer.validated_data['is_new']:
        try:
            user_id = User.objects.only('id').get(phone=phone).id
        except User.DoesNotExist:
            raise NotFound()
        token = token_storage.get_or_create(user_id)
        return Response({'user_id': user_id, 'token': token}, status.HTTP_200_OK)
    serializer = NewUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status.HTTP_201_CREATED)
