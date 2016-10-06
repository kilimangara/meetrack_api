from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .serializers import PhoneNumberSerializer
from rest_framework.decorators import api_view
from django_redis import get_redis_connection

User = get_user_model()


@api_view(['POST'])
def send_code(request):
    serializer = PhoneNumberSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    phone = serializer.validated_data['phone']
    conn = get_redis_connection()
    print(conn.set('hello', 'world'))
    print(conn.get('hello'))
    print(conn.get('world'))
    return Response()
