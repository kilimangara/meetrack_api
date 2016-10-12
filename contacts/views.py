from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImportContactSerializer,DeleteContactsSerializer
from users.serializers import UserSerializer


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contacts(request):
    user = request.user
    if request.method == 'PUT':
        serializer = ImportContactSerializer(data=request.data, context={'user': user})
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        users=serializer.save()
    else:
        if request.method=='DELETE':
            serializer=DeleteContactsSerializer(data=request.data,context={'user':user})
            if not serializer.is_valid():
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
            serializer.save()
        # users=user.
