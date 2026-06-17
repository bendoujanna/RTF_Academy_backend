from django.urls import path
from .views import CurrentUserView

urlpatterns = [
    # becomes api/users/me/
    path('me/', CurrentUserView.as_view(), name='current-user'),
]

