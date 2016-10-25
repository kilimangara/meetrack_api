from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from msg_queue import queue

from .models import Meeting
from .serializers import MeetingSerializer, MembersSerializer
from .serializers import MeetingsListTypeSerializer, MeetingUpdateSerializer, ForeignUserIdSerializer

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
            meetings = meetings.filter(completed=False)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        ids_serializer = MembersSerializer(data=request.data, context={'king': user})
        if not ids_serializer.is_valid():
            return Response(ids_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_ids = ids_serializer.validated_data['users']
        serializer = MeetingSerializer(data=request.data, context={'king': user, 'user_ids': user_ids})
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def single_meeting(request, pk):
    user = request.user
    if request.method == 'PATCH':
        try:
            meeting = user.meetings.get(id=pk, completed=False)
        except Meeting.DoesNotExist:
            raise NotFound()
        if user != meeting.king:
            raise PermissionDenied()
        update_serializer = MeetingUpdateSerializer(meeting, data=request.data, partial=True)
        if not update_serializer.is_valid():
            return Response(update_serializer.errors, status.HTTP_400_BAD_REQUEST)
        update_serializer.save()
        queue.send_to_meeting(meeting.id, {'type': 'completed'})
        serializer = MeetingSerializer(meeting, context={'king': user})
        return Response(serializer.data, status.HTTP_200_OK)
    else:
        try:
            meeting = user.meetings.get(id=pk)
        except Meeting.DoesNotExist:
            raise NotFound()
        if request.method == 'GET':
            serializer = MeetingSerializer(meeting)
            return Response(serializer.data, status.HTTP_200_OK)
        elif request.method == 'DELETE':
            meeting.remove_user(user.id)
            queue.send_to_meeting(meeting.id, {'type': 'left', 'user_id': user.id})
            return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def meeting_members(request, pk):
    user = request.user
    try:
        meeting = user.meetings.get(id=pk, completed=False)
    except Meeting.DoesNotExist:
        raise NotFound()
    id_serializer = ForeignUserIdSerializer(data=request.data, context={'viewer': user})
    if not id_serializer.is_valid():
        return Response(id_serializer.errors, status.HTTP_400_BAD_REQUEST)
    user_id = id_serializer.validated_data['user']
    if request.method == 'DELETE':
        if meeting.king != user:
            raise PermissionDenied()
        meeting.remove_user(user_id)
        queue.send_to_meeting(meeting.id, {'type': 'excluded', 'user_id': user_id})
    elif request.method == 'PUT':
        if not user.inbound_blocks.filter(user_from_id=user_id).exists():
            meeting.add_user(user_id)
            queue.send_to_meeting(meeting.id, {'type': 'invited', 'user_id': user_id})
    serializer = MeetingSerializer(meeting)
    return Response(serializer.data, status.HTTP_200_OK)
