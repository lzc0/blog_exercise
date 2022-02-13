#进行users子应用的视图路由
from django.urls import path
from users.views import RegisterView, ImageCodeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    #图片验证码的路由
    path('imagecode/', ImageCodeView.as_view(), name='imagecode')
]

