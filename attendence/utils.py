from datetime import timedelta
from django.utils.timezone import localtime

def update_attendance_summary(attendance):
    from .models import AttendenceSession

    sessions = AttendenceSession.objects.filter(
        attendence=attendance,
        login_time__isnull=False,
        logout_time__isnull=False,
        deleted=False
    )

    if not sessions.exists():
        return

    # Total working time
    total_seconds = sum(
        (s.logout_time - s.login_time).total_seconds()
        for s in sessions
    )

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    attendance.total_working_hour = f"{hours:02d}:{minutes:02d}"

    # Overtime calculation (beyond 8 hours = 28800 seconds)
    overtime_seconds = max(0, total_seconds - (8 * 60 * 60))
    attendance.overtime_minutes = int(overtime_seconds // 60)

    # Latest login/logout
    latest_session = sessions.order_by('-logout_time').first()
    if latest_session:
        local_login = localtime(latest_session.login_time)
        local_logout = localtime(latest_session.logout_time)
        attendance.check_in = local_login.time()
        attendance.check_out = local_logout.time()
        attendance.check_out_date = local_logout.date()

    attendance.save()
