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

meeting_not_found = NotFound("Meeting not found.")
user_not_king = PermissionDenied("Only king of meeting have permission to perform this action.")
INVITED_MSG = 'USER_INVITED'
COMPLETED_MSG = 'MEETING_COMPLETED'
EXCLUDED_MSG = 'USER_EXCLUDED'
LEFT_MSG = 'USER_LEFT'


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def meetings_list(request):
    user = request.user
    if request.method == 'GET':
        choice_serializer = MeetingsListTypeSerializer(data=request.query_params)
        if not choice_serializer.is_valid():
            return Response(choice_serializer.errors, status.HTTP_400_BAD_REQUEST)
        if not choice_serializer.validated_data['completed']:
            meetings = user.meetings.filter(completed=False)
        else:
            meetings = user.meetings.filter(completed=True)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        ids_serializer = MembersSerializer(data=request.data, context={'king': user})
        if not ids_serializer.is_valid():
            return Response(ids_serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_ids = ids_serializer.validated_data['users']
        serializer = MeetingSerializer(data=request.data, context={'king_id': user.id, 'user_ids': user_ids})
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
            raise meeting_not_found
        if user.id != meeting.king_id:
            raise user_not_king
        update_serializer = MeetingUpdateSerializer(meeting, data=request.data, partial=True)
        if not update_serializer.is_valid():
            return Response(update_serializer.errors, status.HTTP_400_BAD_REQUEST)
        update_serializer.save()
        queue.send_to_meeting(meeting.id, COMPLETED_MSG)
        serializer = MeetingSerializer(meeting, context={'king_id': user.id})
        return Response(serializer.data, status.HTTP_200_OK)
    else:
        try:
            meeting = user.meetings.get(id=pk)
        except Meeting.DoesNotExist:
            raise meeting_not_found
        if request.method == 'GET':
            serializer = MeetingSerializer(meeting)
            return Response(serializer.data, status.HTTP_200_OK)
        elif request.method == 'DELETE':
            removed, meeting_exists = meeting.remove_user(user.id)
            if removed and meeting_exists and not meeting.completed:
                queue.send_to_meeting(meeting.id, LEFT_MSG, {'user': user.id, 'king': meeting.king_id})
            return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def meeting_members(request, pk):
    user = request.user
    try:
        meeting = user.meetings.get(id=pk, completed=False)
    except Meeting.DoesNotExist:
        raise meeting_not_found
    id_serializer = ForeignUserIdSerializer(data=request.data, context={'viewer': user})
    if not id_serializer.is_valid():
        return Response(id_serializer.errors, status.HTTP_400_BAD_REQUEST)
    user_id = id_serializer.validated_data['user']
    if request.method == 'DELETE':
        if user.id != meeting.king_id:
            raise user_not_king
        removed, meeting_exists = meeting.remove_user(user_id)
        if removed and meeting_exists:
            queue.send_to_meeting(meeting.id, EXCLUDED_MSG, {'user': user_id})
    elif request.method == 'PUT':
        if not user.inbound_blocks.filter(user_from_id=user_id).exists() and meeting.add_user(user_id):
            queue.send_to_meeting(meeting.id, INVITED_MSG, {'user': user_id})
    serializer = MeetingSerializer(meeting)
    return Response(serializer.data, status.HTTP_200_OK)
