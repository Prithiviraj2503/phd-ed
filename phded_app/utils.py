import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User


def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def split_full_name(full_name):
    full_name = (full_name or '').strip()
    if not full_name:
        return '', ''
    parts = full_name.split(None, 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name


def send_welcome_email(email, password, first_name, role):
    subject = "Welcome to PhdEd – Your account and password"
    body = f"""
Hello {first_name},

Your {role} account on PhdEd has been created.

Login URL: Please use the same site you signed up from and go to the login page.
Email: {email}
Password: {password}

Please sign in and change your password after first login.

Best regards,
PhdEd Team
"""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phded.example.com')
    try:
        send_mail(
            subject=subject.strip(),
            message=body.strip(),
            from_email=from_email,
            recipient_list=[email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def send_course_content_notification(course, professor, content):
    subject = f"New course content added to {course.name}"
    professor_name = professor.get_full_name() or professor.username or professor.email
    body = f"""
Hello,

New content has been added to the course "{course.name}".

Teacher: {professor_name}
Content title: {content.title}
Department: {course.department.name}

Please log in to PhdEd to review the new material.

Best regards,
PhdEd Team
"""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phded.example.com')
    recipient_list = list(
        User.objects.filter(
            profile__role='student',
            profile__department=course.department.name,
        ).exclude(email='').values_list('email', flat=True).distinct()
    )
    if not recipient_list:
        return 0

    sent_count = 0
    for email in recipient_list:
        try:
            send_mail(
                subject=subject,
                message=body.strip(),
                from_email=from_email,
                recipient_list=[email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception:
            continue
    return sent_count


def send_assignment_launch_notification(course, assignment, professor):
    subject = f"Assignment launched: {assignment.title}"
    professor_name = professor.get_full_name() or professor.username or professor.email
    body = f"""
Hello,

A new assignment has been launched in PhdEd.

Course: {course.name}
Assignment: {assignment.title}
Teacher: {professor_name}
Department: {course.department.name}

Please log in to PhdEd to take the assignment.

Best regards,
PhdEd Team
"""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@phded.example.com')
    recipient_list = list(
        User.objects.filter(
            profile__role='student',
            profile__department=course.department.name,
        ).exclude(email='').values_list('email', flat=True).distinct()
    )
    if not recipient_list:
        return 0

    sent_count = 0
    for email in recipient_list:
        try:
            send_mail(
                subject=subject,
                message=body.strip(),
                from_email=from_email,
                recipient_list=[email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception:
            continue
    return sent_count
