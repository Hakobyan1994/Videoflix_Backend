from .serializers import RegisterSerializer,CookieTokenObtainPairSerializer,PasswordResetSerializer,SetNewPasswordSerializer
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from .utils import send_activation_email,send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views  import   TokenObtainPairView, TokenRefreshView



class RegisterView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            send_activation_email(request, user)
            return Response({
                'user_id': user.id,
                'email': user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


User = get_user_model()
class ActivateAccountView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Konto erfolgreich aktiviert!"}, status=status.HTTP_200_OK)
        return Response({"error": "Ungültiger oder abgelaufener Aktivierungslink."}, status=status.HTTP_400_BAD_REQUEST)   



class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class=CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh=serializer.validated_data.get("refresh")
        access=serializer.validated_data.get("access")

        response = Response({"message": "Login erfolgreich"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        response.data={'message':'Login erfolgreich'}
        return response        
    

class  CookieTokenRefreshView(TokenRefreshView):
     

   def post(self, request, *args, **kwargs):
     refresh_token = request.COOKIES.get("refresh_token")
     if not refresh_token:
            return Response({"error": "Kein Refresh-Token gefunden."}, status=status.HTTP_400_BAD_REQUEST)
     serializer=self.get_serializer(data={"refresh": refresh_token})
     if serializer.is_valid():
         access_token = serializer.validated_data.get("access")
         response = Response({"message": "Access-Token erfolgreich erneuert."}, status=status.HTTP_200_OK)        
         response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax"
            )
         return response            
     else:
         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     





class PasswordResetView(APIView):
    authentication_classes = [] 
    permission_classes=[AllowAny]

    def post(self, request):
        serializer=PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        user=User.objects.get(email=email)
        send_password_reset_email(request,user)
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
    

class PasswordResetConfirmView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    


class LogouthView(APIView):
   
    def post(self,request):
        response = Response({"message": "Erfolgreich ausgeloggt."}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response