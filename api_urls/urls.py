from django.urls import path
from user_auth.api.views import RegisterView,ActivateAccountView,CookieTokenObtainPairView,CookieTokenRefreshView,PasswordResetConfirmView,PasswordResetView,LogouthView
from videos.api.views import VideoList,VideoDetail,serve_hls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/',CookieTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('video/', VideoList.as_view(), name='video-list'),
    path('video/<int:pk>/', VideoDetail.as_view(), name='video-detail'),
    path("video/<int:video_id>/<str:suffix>/<str:filename>", serve_hls,  name="video-hls", ),
    path('logout/',LogouthView.as_view(),name='logout')
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    