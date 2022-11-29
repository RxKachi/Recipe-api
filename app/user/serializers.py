from django.contrib.auth import get_user_model
from rest_framework import serializers

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class UserSerializer(serializers.ModelSerializer):
    '''serializes the user model'''
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        '''create and return a new user with encrypted password'''
        return get_user_model().objects.create_user(**validated_data)


# class UserLoginSerializer(serializers.ModelSerializer):
#     '''serializer for user login token generation'''
#     class Meta:
#         model = get_user_model()
#         fields = ('email', 'password')
#         extra_kwargs = {
#             'password': {
#                 'min_length': 5
#             }
#         }


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
