from rest_framework import serializers
from user_auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirmed_password =serializers.CharField(write_only=True)
    

    class Meta:
        model=User
        fields=['email','password','confirmed_password']
        extra_kwargs={
            'email':{
                'required':True
            }
        }


    def validate(self,data):
      required_fields = ['email', 'password', 'confirmed_password']
      for field in required_fields:
            if field not in data:
                raise serializers.ValidationError({field: [f'{field} is required.']})
      if len(data['password']) < 6: 
          raise serializers.ValidationError({'password': ['Password must be at least 6 characters long.']})
      if data['password'] != data['confirmed_password']:
          raise serializers.ValidationError({'password': ['Passwords dont match.']}) 
      if User.objects.filter(email=data['email']).exists():
          raise serializers.ValidationError({'email': ['Email is already in use.']})
      return data


    
    def create(self, validated_data):
     validated_data.pop('confirmed_password')
     email = validated_data['email']  
     password = validated_data['password'] 

     user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        is_active=False
    )

     return user
    



from django.contrib.auth import get_user_model
User=get_user_model()

class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        if "username" in self.fields:
            self.fields.pop("username")


    def validate(self, attrs):
        email=attrs.get("email")      
        password = attrs.get("password")

        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Benutzer mit dieser E-Mail existiert nicht.")     
        
        if not user.check_password(password):
            raise serializers.ValidationError("Falsches Passwort.")

        attrs['username']=user.username
        data=super().validate(attrs)
        return data
    


class PasswordResetSerializer(serializers.Serializer): 
    email=serializers.EmailField()

    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
             raise serializers.ValidationError("No user found with this email.")
        return value



class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
