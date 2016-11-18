from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from base_app.error_types import MEETING_NOT_FOUND, YOU_NOT_KING, USER_NOT_FOUND, USER_BLOCKED_YOU, MEETING_NOT_ACTIVE
from base_app.response import SuccessResponse, ErrorResponse
from base_app.serializers import ForeignUserIdSerializer
from msg_queue import queue
from .models import Meeting
from .msg_types import USER_EXCLUDED, USER_INVITED, USER_LEFT, MEETING_COMPLETED
from .serializers import MeetingSerializer, MembersSerializer
from .serializers import MeetingsListTypeSerializer, MeetingUpdateSerializer

User = get_user_model()


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def meetings_list(request):
    user = request.user
    if request.method == 'GET':
        choice_serializer = MeetingsListTypeSerializer(data=request.query_params)
        choice_serializer.is_valid(raise_exception=True)
        if not choice_serializer.validated_data['completed']:
            meetings = user.meetings.filter(completed=False)
        else:
            meetings = user.meetings.filter(completed=True)
        serializer = MeetingSerializer(meetings, many=True)
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        ids_serializer = MembersSerializer(data=request.data, context={'king': user})
        ids_serializer.is_valid(raise_exception=True)
        user_ids = ids_serializer.validated_data['users']
        serializer = MeetingSerializer(data=request.data, context={'king_id': user.id, 'user_ids': user_ids})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def single_meeting(request, pk):
    user = request.user
    try:
        meeting = user.meetings.get(id=pk)
    except Meeting.DoesNotExist:
        return ErrorResponse(MEETING_NOT_FOUND, status.HTTP_404_NOT_FOUND,
                             "Your meeting with that id does not exist.")
    if request.method == 'PATCH':
        if meeting.completed:
            return ErrorResponse(MEETING_NOT_ACTIVE, status.HTTP_404_NOT_FOUND, "The meeting has been completed.")
        if user.id != meeting.king_id:
            return ErrorResponse(YOU_NOT_KING, status.HTTP_403_FORBIDDEN,
                                 "Only the king of meeting can update the meeting.")
        update_serializer = MeetingUpdateSerializer(meeting, data=request.data, partial=True)
        update_serializer.is_valid(raise_exception=True)
        update_serializer.save()
        queue.send_to_meeting(meeting.id, MEETING_COMPLETED)
        serializer = MeetingSerializer(meeting, context={'king_id': user.id})
        return SuccessResponse(serializer.data, status.HTTP_200_OK)
    else:
        if request.method == 'GET':
            serializer = MeetingSerializer(meeting)
            return SuccessResponse(serializer.data, status.HTTP_200_OK)
        elif request.method == 'DELETE':
            removed, meeting_exists = meeting.remove_user(user.id)
            if removed and meeting_exists and not meeting.completed:
                queue.send_to_meeting(meeting.id, USER_LEFT, {'user': user.id, 'king': meeting.king_id})
            return SuccessResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def meeting_members(request, pk):
    user = request.user
    try:
        meeting = user.meetings.get(id=pk)
    except Meeting.DoesNotExist:
        return ErrorResponse(MEETING_NOT_FOUND, status.HTTP_404_NOT_FOUND,
                             "Your meeting with that id does not exist.")
    if meeting.completed:
        return ErrorResponse(MEETING_NOT_ACTIVE, status.HTTP_404_NOT_FOUND, "The meeting has been completed.")
    id_serializer = ForeignUserIdSerializer(data=request.data, context={'viewer': user})
    id_serializer.is_valid(raise_exception=True)
    user_id = id_serializer.validated_data['user']
    if not User.objects.filter(id=user_id).exists():
        return ErrorResponse(USER_NOT_FOUND, status.HTTP_404_NOT_FOUND, "Cannot find user with that id.")
    if request.method == 'DELETE':
        if user.id != meeting.king_id:
            return ErrorResponse(YOU_NOT_KING, status.HTTP_403_FORBIDDEN,
                                 "Only the king of meeting can exclude participants.")
        removed, meeting_exists = meeting.remove_user(user_id)
        if removed and meeting_exists:
            queue.send_to_meeting(meeting.id, USER_EXCLUDED, {'user': user_id})
    elif request.method == 'PUT':
        if user.inbound_blocks.filter(user_from_id=user_id).exists():
            return ErrorResponse(USER_BLOCKED_YOU, status.HTTP_403_FORBIDDEN, "User added you to the blacklist.")
        added = meeting.add_user(user_id)
        if added:
            queue.send_to_meeting(meeting.id, USER_INVITED, {'user': user_id})
    serializer = MeetingSerializer(meeting)
    return SuccessResponse(serializer.data, status.HTTP_200_OK)
