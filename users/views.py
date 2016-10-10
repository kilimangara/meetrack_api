from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .serializers import UserSerializer, UsersIdsSerializer, ForeignUserSerializer

User = get_user_model()


@api_view(['PATCH', 'GET'])
@permission_classes([IsAuthenticated])
def account(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    ids_serializer = UsersIdsSerializer(data=request.query_params)
    if not ids_serializer.is_valid():
        return Response(ids_serializer.errors, status.HTTP_400_BAD_REQUEST)

    matched_users = ids_serializer.registered_users()
    serializer = ForeignUserSerializer(matched_users, context={'viewer': request.user}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise NotFound()
    if user != request.user:
        serializer = ForeignUserSerializer(user, context={'viewer': request.user})
    else:
        serializer = UserSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)
