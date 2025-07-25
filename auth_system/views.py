from django.shortcuts import render
from .serializer import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.db.models import F, Value
from django.db.models.functions import Concat
from rest_framework.authentication import BaseAuthentication
from .models import BlacklistToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth.models import User
from . import exception as e
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny
from datetime import datetime, date
from api.models import *
from attendence.models import *
from django.utils.timezone import now as tz_now
from django.utils import timezone


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise e.CustomAuthenticationFailed(detail="Authentication credentials were not provided.")

        try:
            token = auth_header.split('Bearer ')[1]
        except IndexError:
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        if BlacklistToken.objects.filter(token=token).exists():
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
        except Exception:
            raise e.CustomAuthenticationFailed(detail='Your session has expired. Please log in again.')

        return (user, token)

class AllowAnyView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

class RegisterView(AllowAnyView):
    def post(self, request):
        try:
            data = request.data

            if data.get('password') != data.get('confirm_password'):
                return Response({"error": "Passwords do not match.", "status": 400}, status=400)

            if User.objects.filter(username=data.get('username')).exists():
                return Response({"error": "Username already exists.", "status": 400}, status=400)

            if User.objects.filter(email=data.get('email')).exists():
                return Response({"error": "Email already exists.", "status": 400}, status=400)

            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()

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

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request):
        try:
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
            response.delete_cookie('refreshToken', path='/', domain='your-domain.com')
            response.data = {
                "data": "Your session has expired. Please log in again.",
                "status": 500
            }
            return response
        

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'data': "Email and password are required.", "status": 400}, status=400)

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)

            if user is None:
                return Response({'data': "Invalid credentials.", "status": 401}, status=401)

            refresh = RefreshToken.for_user(user)
            mobile = user.username if not user.username.isdigit() else int(user.username)

            user_data = {
                "username": user.username,
                "email": user.email,
                "f_name": user.first_name,
                "l_name": user.last_name,
                "mobile": mobile,
            }

            # === Attendance Check-in and Session ===
            try:
                employee = Employee.objects.get(user=user, deleted=False)
                today = date.today()
                now = timezone.now()
                status = AttendenceStatus.objects.get(name__iexact="present", deleted=False)

                attendence, created = Attendence.objects.get_or_create(
                    employee=employee,
                    check_in_date=today,
                    defaults={
                        "check_in": now.time(),
                        "status": status
                    }
                )

                if not created and not attendence.check_in:
                    attendence.check_in = now.time()
                    attendence.status = status
                    attendence.save()

                # Close any previously open session
                last_session = AttendenceSession.objects.filter(
                    attendence=attendence,
                    logout_time__isnull=True
                ).order_by('-login_time').first()

                if last_session:
                    last_session.logout_time = now
                    last_session.save()

                # Create new session
                AttendenceSession.objects.create(
                    attendence=attendence,
                    login_time=now
                )

            except Exception as ex:
                print("⚠️ Attendance/session error on login:", ex)

            # === Response ===
            response = Response({
                "token": str(refresh.access_token),
                "user": [user_data],
                "status": 200
            })

            response.set_cookie(
                key='refreshToken',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='None'
            )

            return response

        except Exception as e:
            return Response({
                'data': f"An error occurred during login: {str(e)}",
                "status": 500
            })


class LogoutView(APIView):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or 'Bearer ' not in auth_header:
                return Response({"data": "Invalid token format.", "status": 401})

            token = auth_header.split('Bearer ')[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            if BlacklistToken.objects.filter(token=token).exists():
                return Response({"data": "Already logged out.", "status": 403})

            # Get employee
            employee = Employee.objects.get(user_id=user_id, deleted=False)
            today = date.today()
            now = timezone.now()

            # Get today's attendance
            attendence = Attendence.objects.filter(
                employee=employee,
                check_in_date=today,
                deleted=False
            ).first()

            if attendence:
                # Find the latest session that's still open
                open_session = AttendenceSession.objects.filter(
                    attendence=attendence,
                    logout_time__isnull=True,
                    deleted=False
                ).order_by('-login_time').first()

                if open_session:
                    open_session.logout_time = now
                    open_session.save()

                # 🧠 Recalculate total working hours from all sessions
                all_sessions = AttendenceSession.objects.filter(
                    attendence=attendence,
                    login_time__isnull=False,
                    logout_time__isnull=False,
                    deleted=False
                )

                total_seconds = sum(
                    (s.logout_time - s.login_time).total_seconds()
                    for s in all_sessions
                )

                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)

                attendence.total_working_hour = f"{hours:02d}:{minutes:02d}"

                # 🕓 Update check_out and check_out_date using last session
                last_session = all_sessions.order_by('-logout_time').first()
                if last_session:
                    attendence.check_out = last_session.logout_time.time()
                    attendence.check_out_date = last_session.logout_time.date()

                attendence.save()
            else:
                print("⚠️ No attendance found for today")

            # 🔒 Blacklist token
            BlacklistToken.objects.create(token=token)

            response = Response()
            response.delete_cookie('refreshToken', path='/', domain='your-domain.com')
            response.data = {"data": "User logout successfully.", "status": 200}
            return response

        except Exception as e:
            return Response({
                "data": f"Something went wrong during logout: {str(e)}",
                "status": 500
            })
