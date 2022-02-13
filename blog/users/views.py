from django.shortcuts import render

# Create your views here.

#注册视图
from django.views import View



class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

from django.http.response import HttpResponseBadRequest
from django_redis import get_redis_connection
from django.http import HttpResponse
from libs.captcha.captcha import captcha
class ImageCodeView(View):

    def get(self, request):

        #接受uuid
        uuid = request.GET.get('uuid')
        #判断是否获取uuid
        if uuid is None:
            return HttpResponseBadRequest('未传递uuid')
        #调用captcha生成图片验证码
        text, image = captcha.generate_captcha()
        #将图片内容保存到redis,uuid为key,图片为value
        redis_conn = get_redis_connection('default')
        #key,seconds,value
        redis_conn.setex('img:%s' % uuid, 300, text)
        #返回图片二进制
        return HttpResponse(image, content_type='image/jpeg')
