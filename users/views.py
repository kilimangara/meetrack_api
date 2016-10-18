from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import AccountSerializer, UserSerializer
from .serializers import ImportContactsSerializer, DeleteContactsSerializer, UserIdsSerializer, ForeignUserIdSerializer

User = get_user_model()


@api_view(['PATCH', 'GET', 'DELETE'])
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
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        id_serializer = ForeignUserIdSerializer(data=request.data, context={'viewer': user})
        if not id_serializer.is_valid():
            return Response(id_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_id = id_serializer.validated_data['user_id']
        if request.method == 'PUT':
            user.add_to_blacklist(user_id)
        else:
            user.remove_from_blacklist(user_id)
    serializer = UserSerializer(user.blocked_users(), context={'viewer': user}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contacts(request):
    user = request.user
    if request.method == 'PUT':
        serializer = ImportContactsSerializer(data=request.data, context={'user': user})
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        users = user.add_to_contacts(serializer.validated_data['phones'], serializer.validated_data['names'])
    else:
        if request.method == 'DELETE':
            serializer = DeleteContactsSerializer(data=request.data, context={'user': user})
            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            user.remove_from_contacts(serializer.validated_data['phones'])
        users = user.contacted_users
    serializer = UserSerializer(users, context={'viewer': user}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)
