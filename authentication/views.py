from django.contrib.auth import get_user_model
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
    serializer.send_code()
    phone = serializer.validated_data['phone']
    is_new = not User.objects.filter(phone=phone).exists()
    return Response({'is_new': is_new}, status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    phone_serializer = ConfirmPhoneSerializer(data=request.data)
    if not phone_serializer.is_valid():
        return Response(phone_serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = phone_serializer.validated_data['phone']
    if not phone_serializer.validated_data['is_new']:
        try:
            user_id = User.objects.only('id').get(phone=phone).id
        except User.DoesNotExist:
            raise NotFound()
    else:
        user_serializer = NewUserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_id = user_serializer.save().id
    token = token_storage.create(user_id)
    return Response({'token': token, 'user_id': user_id}, status.HTTP_201_CREATED)
