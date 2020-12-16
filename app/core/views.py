from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views import View
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.core.models import User, Reminder
from app.core.permissions import CanManageReminder, PermissionModelMixin, CanAccessReminder
from app.core.serializers import SignUpSerializer, ReminderCreateSerializer, ReminderRetrieveSerializer, \
    UserDetailedSerializer, ReminderEditSerializer
from app.core.utils import TokenCrypter


class VerifyEmail(View):
    def get(self, *args, **kwargs):
        token = self.request.GET.get('token')
        try:
            data = TokenCrypter.get_data_from_code(token)
            if data.get('type') == 'email_activate':
                user = User.objects.get(pk=data.get('user_id'))
                user.is_active = True
                user.save()
                return redirect('/login?result=success')
        except Exception:
            pass
        finally:
            return redirect('/login?result=error')


class SignUp(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = get_user_model().objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailedSerializer

    @action(methods=['GET'], detail=False)
    def me(self, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ReminderViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      PermissionModelMixin,
                      GenericViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderRetrieveSerializer
    permission_classes = [IsAuthenticated]

    permission_classes_by_action = {'destroy': [CanManageReminder],
                                    'complete': [CanManageReminder],
                                    'retrieve': [CanAccessReminder],
                                    'edit': [CanManageReminder],
                                    }

    def get_serializer_class(self):
        if self.action == 'create':
            return ReminderCreateSerializer
        elif self.action == 'retrieve':
            return ReminderRetrieveSerializer
        elif self.action == 'edit':
            return ReminderEditSerializer
        elif self.action == 'complete':
            return ReminderRetrieveSerializer
        elif self.action == 'my':
            return ReminderRetrieveSerializer
        elif self.action == 'assigned':
            return ReminderRetrieveSerializer
        return super(ReminderViewSet, self).get_serializer_class()

    @action(detail=True, methods=['POST'])
    def complete(self, request, *args, **kwargs):
        reminder = self.get_object()
        reminder.is_completed = True
        reminder.save()
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def edit(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, instance=self.get_object(), partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def my(self, request, *args, **kwargs):
        reminders_queryset = Reminder.objects.filter(creator=self.request.user)
        serializer = self.get_serializer(reminders_queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def assigned(self, request, *args, **kwargs):
        user = self.request.user
        reminders_queryset = user.reminder_set.all()
        serializer = self.get_serializer(reminders_queryset, many=True)
        return Response(serializer.data)
