from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base_app.error_types import USER_NOT_FOUND
from base_app.response import SuccessResponse, ErrorResponse
from base_app.serializers import ForeignUserIdSerializer
from users.models import User
from .serializers import AccountSerializer, UserSerializer
from .serializers import ImportContactsSerializer, DeleteContactsSerializer, UserIdsSerializer


@api_view(['PATCH', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def account(request):
    user = request.user
    if request.method == 'GET':
        serializer = AccountSerializer(user)
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = AccountSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        user.delete()
        return SuccessResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    ids_serializer = UserIdsSerializer(data=request.query_params)
    ids_serializer.is_valid(raise_exception=True)
    user_ids = ids_serializer.validated_data['users']
    users = User.objects.filter(id__in=user_ids).distinct('id')
    serializer = UserSerializer(users, viewer=request.user, many=True)
    return SuccessResponse(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return ErrorResponse(USER_NOT_FOUND, status.HTTP_404_NOT_FOUND, "User with such id does not exist.")
    serializer = UserSerializer(user, viewer=request.user)
    return SuccessResponse(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def blacklist(request):
    user = request.user
    if request.method != 'GET':
        id_serializer = ForeignUserIdSerializer(data=request.data, context={'viewer': user})
        id_serializer.is_valid(raise_exception=True)
        user_id = id_serializer.validated_data['user']
        if not User.objects.filter(id=user_id).exists():
            return ErrorResponse(USER_NOT_FOUND, status.HTTP_404_NOT_FOUND, "User with such id does not exist.")
        if request.method == 'PUT':
            user.blocks.get_or_create(user_to_id=user_id)
        else:
            user.remove_from_blacklist(user_id)
    serializer = UserSerializer(user.blocked_users, viewer=user, many=True)
    return SuccessResponse(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contacts(request):
    user = request.user
    if request.method == 'PUT':
        import_serializer = ImportContactsSerializer(data=request.data, context={'user': user})
        import_serializer.is_valid(raise_exception=True)
        contacted_users = user.add_to_contacts(import_serializer.validated_data['phones'],
                                               import_serializer.validated_data['names'])
        serializer = UserSerializer(contacted_users, viewer=request.user, many=True)
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    elif request.method == 'GET':
        serializer = UserSerializer(user.contacted_users, viewer=request.user, many=True)
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        delete_serializer = DeleteContactsSerializer(data=request.data, context={'user': user})
        delete_serializer.is_valid(raise_exception=True)
        phones = delete_serializer.validated_data.get('phones')
        user_ids = delete_serializer.validated_data.get('users')
        result_filter = None
        if user_ids:
            user_ids_filter = Q(user_to_id__in=user_ids)
            result_filter = user_ids_filter
        if phones:
            phones_filter = Q(phone__in=phones, user_to__isnull=True)
            result_filter = result_filter | phones_filter if result_filter is not None else phones_filter
        if result_filter is not None:
            user.contacts.filter(result_filter).distinct('id').delete()
        return SuccessResponse(status=status.HTTP_204_NO_CONTENT)
