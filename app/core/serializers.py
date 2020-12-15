from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from app.core.tasks import confirm_email, send_reminder_email
from app.core.models import User, Reminder


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
        ]

    def validate(self, attrs):
        attrs = super(SignUpSerializer, self).validate(attrs)
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({'email': 'User with this email already exists'})
        return attrs

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        confirm_email.delay(user.id)
        return user

    def to_representation(self, instance):
        return {
            'token': jwt_encode_handler(jwt_payload_handler(instance))
        }


class UserDetailedSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class ReminderCreateSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    participants = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=True)

    class Meta:
        model = Reminder
        fields = (
            'creator',
            'header',
            'description',
            'place',
            'participants',
            'date_to_complete',
        )

    def create(self, validated_data):
        reminder = self.Meta.model.objects.create(
            creator=validated_data.get('creator'),
            header=validated_data.get('header'),
            description=validated_data.get('description'),
            place=validated_data.get('place'),
            date_to_complete=validated_data.get('date_to_complete'),
        )
        participants = User.objects.filter(id__in=validated_data.get('participants')).values_list('id', flat=True)
        reminder.participants.add(*participants)
        participants = list(participants)
        participants.append(reminder.creator_id)
        send_reminder_email.apply_async([participants, reminder.id], eta=reminder.date_to_complete)
        return reminder

    def to_representation(self, instance):
        return ReminderRetrieveSerializer(instance).data


class ReminderRetrieveSerializer(serializers.ModelSerializer):
    creator = UserDetailedSerializer()
    participants = UserDetailedSerializer(many=True, required=False)

    class Meta:
        model = Reminder
        fields = (
            'header',
            'description',
            'place',
            'date_created',
            'date_to_complete',
            'creator',
            'participants',
            'is_completed',
        )


class ReminderEditSerializer(serializers.ModelSerializer):
    participants_to_add = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=True)
    participants_to_remove = serializers.ListField(child=serializers.IntegerField(), allow_empty=True, required=True)

    class Meta:
        model = Reminder
        fields = (
            'header',
            'description',
            'place',
            'date_to_complete',
            'participants_to_add',
            'participants_to_remove',
        )

    def update(self, instance, validated_data):
        if validated_data.get('participants_to_add'):
            participants_to_add = validated_data.pop('participants_to_add')
            participants = User.objects.filter(id__in=participants_to_add).values_list('id', flat=True)
            instance.participants.remove(*participants)
        if validated_data.get('participants_to_remove'):
            participants_to_remove = validated_data.pop('participants_to_remove')
            participants = User.objects.filter(id__in=participants_to_remove).values_list('id', flat=True)
            instance.participants.remove(*participants)
        instance = super(ReminderEditSerializer, self).update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return ReminderRetrieveSerializer(instance).data
