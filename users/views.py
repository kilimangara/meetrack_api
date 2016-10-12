from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .serializers import AccountSerializer, UserIdsSerializer, UserSerializer

User = get_user_model()


@api_view(['PATCH', 'GET'])
@permission_classes([IsAuthenticated])
def account(request):
    user = request.user
    if request.method == 'GET':
        serializer = AccountSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = AccountSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    ids_serializer = UserIdsSerializer(data=request.query_params)
    if not ids_serializer.is_valid():
        return Response(ids_serializer.errors, status.HTTP_400_BAD_REQUEST)
    matched_users = ids_serializer.registered_users()
    serializer = UserSerializer(matched_users, context={'viewer': request.user}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise NotFound()
    serializer = UserSerializer(user, context={'viewer': request.user})
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def blacklist(request):
    user = request.user
    if request.method != 'GET':
        ids_serializer = UserIdsSerializer(data=request.data)
        if not ids_serializer.is_valid():
            return Response(ids_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_ids = ids_serializer.registered_user_ids()
        if request.method == 'PUT':
            user.put_into_blacklist(user_ids)
        else:
            user.remove_from_blacklist(user_ids)
    serializer = UserSerializer(user.blacklist, context={'viewer': user}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)
