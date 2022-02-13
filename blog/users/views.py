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


from django.http.response import JsonResponse
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('django')
from random import randint
from libs.yuntongxun.sms import CCP
class SmsCodeView(View):

    def get(self, request):

        #接收参数
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        #参数的验证
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要参数'})
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get('img:%s' % uuid)
        if redis_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已过期'})
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码错误'})
        #生成短信验证码
        sms_code = '%06d'% randint(0, 999999)
        logger.info(sms_code)
        #保存短信验证码到redis
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        #发送短信
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        #返回响应
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})