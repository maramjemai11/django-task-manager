from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, RegisterView
from django.urls import path

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = router.urls
urlpatterns += [
    path('register/', RegisterView.as_view(), name='api_register'),
]
