from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import MeetingSerializer, MeetingsListTypeSerializer

User = get_user_model()


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def meetings_list(request):
    user = request.user
    if request.method == 'GET':
        choice_serializer = MeetingsListTypeSerializer(data=request.query_params)
        if not choice_serializer.is_valid():
            return Response(choice_serializer.errors, status.HTTP_400_BAD_REQUEST)
        meetings = user.meetings
        if not choice_serializer.validated_data['all']:
            meetings.filter(completed=False)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        pass
