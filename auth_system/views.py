from django.shortcuts import render
from .serializer import *
from rest_framework_simplejwt.views import TokenRefreshView
# from api.models import Employee
from django.db.models import F,Value
from django.db.models.functions import Concat
# import random,requests,urllib
from rest_framework.authentication import BaseAuthentication
from .models import BlacklistToken
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from django.contrib.auth.models import User
from . import exception as e
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny


# Create your views here.

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise e.CustomAuthenticationFailed(detail="Authentication credentials were not provided.")

        try:
            token = auth_header.split('Bearer ')[1]
        except IndexError:
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        # Check if token is blacklisted
        if BlacklistToken.objects.filter(token=token).exists():
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        # Validate the token
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
        except Exception:
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        return (user, token)
    

class AllowAnyView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

#register view
class RegisterView(AllowAnyView):
    def post(self, request):
        try:
            data = request.data

            # Manual validation
            if data.get('password') != data.get('confirm_password'):
                return Response({"error": "Passwords do not match.", "status": 400}, status=400)

            if User.objects.filter(username=data.get('username')).exists():
                return Response({"error": "Username already exists.", "status": 400}, status=400)

            if User.objects.filter(email=data.get('email')).exists():
                return Response({"error": "Email already exists.", "status": 400}, status=400)

            # Proceed with serializer
            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                try:
                    mobile = int(user.username)
                except (ValueError, TypeError):
                    mobile = user.username

                user_data = {
                    "username": user.username,
                    "email": user.email,
                    "f_name": user.first_name,
                    "l_name": user.last_name,
                    "mobile": mobile,
                }

                # Prepare response with refresh token as cookie
                response = Response({
                    "token": str(refresh.access_token),
                    "user": user_data,
                    "status": 200,
                    "message": "User registered successfully"
                }, status=200)

                response.set_cookie(
                    key='refreshToken',
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite='None'
                )
                return response

            return Response({"data": serializer.errors, "status": 400}, status=400)

        except Exception as e:
            return Response({
                "data": f"An error occurred during registration: {str(e)}",
                "status": 500
            }, status=500)
        
# Login view
User = get_user_model()

class LoginView(AllowAnyView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'data': "Email and password are required.", "status": 400}, status=400)

        try:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'data': "Invalid credentials.", "status": 401}, status=401)

            user = authenticate(username=user_obj.username, password=password)

            if user is None:
                return Response({'data': "Invalid credentials.", "status": 401}, status=401)

            refresh = RefreshToken.for_user(user)
            try:
                mobile = int(user.username)
            except (ValueError, TypeError):
                mobile = user.username

            user_data = {
                "username": user.username,
                "email": user.email,
                "f_name": user.first_name,
                "l_name": user.last_name,
                "mobile": mobile,
            }

            response = Response({
                "token": str(refresh.access_token),
                "user": [user_data],
                "status": 200
            })

            response.set_cookie(
                key='refreshToken',
                value=str(refresh),  #gives refresh token
                httponly=True,
                secure=True,
                samesite='None'
            )

            return response

        except Exception as e:
            return Response({'data': f"An error occurred during login: {str(e)}", "status": 500}, status=500)     

#refresh token view
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request):
        try:
            # READ COOKIE HERE - This is how we get the refresh token
            refresh_token = request.COOKIES.get('refreshToken')
            access_token = RefreshToken(refresh_token).access_token
            
            response = Response()
            response.data = {
                "access_token": str(access_token),
                "status": 200
            }
            return response
        except:
            response = Response(status=401)
            # DELETE COOKIE HERE - Clear invalid cookie
            response.delete_cookie('refreshToken', path='/', domain='your-domain.com')
            response.data = {
                "data": "Your session has expired. Please log in again.",
                "status": 500
            }
            return response
        

#logout view
class LogoutView(APIView):
    def post(self, request):
        try:
            response = Response()
            # DELETE COOKIE HERE - Remove the refresh token
            response.delete_cookie('refreshToken', path='/', domain='your-domain.com')
            
            token = request.headers.get('Authorization').split('Bearer ')[1]
            response.data = {"data": "User logout successfully.", "status": 200}
            
            if BlacklistToken.objects.filter(token=token).exists():
                return Response({"data": "User logout successfully.", "status": 500})
            
            # Blacklist the access token
            BlacklistToken.objects.create(token=token)
            return response
        except:
            return Response({"data": "Something went wrong while logout!", "status": 500})