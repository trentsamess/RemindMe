from django.urls import path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from app.core.views import SignUp, ReminderViewSet, UserViewSet, VerifyEmail

router = SimpleRouter()
router.register('reminder', ReminderViewSet, 'reminders')
router.register('user', UserViewSet, 'users')

urlpatterns = [
    path('auth/signup/', SignUp.as_view(), name='signup'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmail.as_view()),
]


urlpatterns += router.urls
