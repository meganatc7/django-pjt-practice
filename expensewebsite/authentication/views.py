from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)
    
    def run(self):
        self.email_message.send(fail_silently=False)


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'sorry email in use, choose another one'}, status=409)
        return JsonResponse({'email_valid': True})

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'sorry username in use, choose another one'}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST,
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                
                # Base64 방식: A-Z, a-z, 0-9, +, / 총 64개의 문자를 기반으로 표현하는 방식
                # 즉 user.pk를 바이트 타입으로 변환하고 base64방식으로 인코딩
                # user.pk는 자연수 값이며 이를 force_byte를 통해 bytes로 바꿔줌
                # 그리고 urlsafe_base64_encode로 인코딩
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                # 현재 서버의 도메인을 만들고
                # get_current_site는 request를 보낸 site를 알려줌
                domain = get_current_site(request).domain
                
                # 링크를 만들고
                # reverse 첫 번째 인자: url name, kwargs에는 path에 구성해준대로 알맞게
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})
                
                # 최종 링크를 만들고
                activate_url = 'http://' + domain + link

                # 이메일 내용 보내기
                email_body = 'Hi'+user.username+'Please use this link to verify your account\n' + activate_url
                email_subject = "Activate your account"
                email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@semycolon.com',
                            [email],
                        )
                # email.send(fail_silently=False)

                EmailThread(email).start()

                messages.success(request, 'Account successfully created')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if user is not None and token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('login' + '?message=' + 'User already activated')

            if user.is_active:
                return redirect('login')

            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request, 'Welcome, ' + user.username + ' You are now logged in')
                    return redirect('expenses')

                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']

        context = {
            'fieldValues': request.POST
        }
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset-password.html', context)
        
        current_site = get_current_site(request)
        user = User.objects.get(email=email)
        print('유저', user)
        if user:
            email_contents = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': PasswordResetTokenGenerator.make_token(user),
            }

            link = reverse('reset-user-password', kwargs={
                'uidb64': email_contents['uid'], 'token': email_contents['token']
            })

            email_subject = 'Password reset Instructions'

            reset_url = 'http://' + current_site.domain + link

            email = EmailMessage(
                email_subject,
                'Hi there, Please the click linke below to reset your password \n' + reset_url,
                'meganatc7@gmail.com',
                [email],
            )
            EmailThread(email).start()
        messages.success(request, 'We have sent you an email to reset your password')

    
class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):

                messages.info(request, 'Password link is invalid, please request a new one')
                return render(request, 'authentication/reset-password.html')
        except Exception as identifier:
            pass

        return render(request, 'authentication/set-newpassword.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request,'Passwords do not match')
            return render(request, 'authentication/set-newpassword.html', context)
        
        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-newpassword.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfully, you can login with your new password')
            return redirect('login')
        except Exception as identifier:
            messages.info(request, 'Something wrong, try again')
            return render(request, 'authentication/set-newpassword.html', context)

        # return render(request, 'authentication/set-newpassword.html', context)