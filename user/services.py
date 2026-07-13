from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class AccountCreationError(Exception):
    def __init__(self, messages):
        self.messages = messages
        super().__init__(' '.join(messages))


def create_student_account(email, password, full_name='', phone='', current_level=''):
    email = (email or '').strip()
    full_name = (full_name or '').strip()
    phone = (phone or '').strip()
    current_level = (current_level or '').strip()

    if not email or not password:
        raise AccountCreationError(['Email and password are required.'])

    if User.objects.filter(email=email).exists():
        raise AccountCreationError(['An account with this email already exists.'])

    try:
        validate_password(password)
    except ValidationError as e:
        raise AccountCreationError(list(e.messages))

    username = email.split('@')[0]
    base_username = username
    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{suffix}'
        suffix += 1

    first_name = full_name.split(' ')[0] if full_name else ''
    last_name = ' '.join(full_name.split(' ')[1:]) if full_name else ''

    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        current_level=current_level,
    )


def create_teacher_application(email, password, full_name='', phone=''):
    user = create_student_account(email, password, full_name=full_name, phone=phone)
    user.role = 'teacher'
    user.is_active = False
    user.save(update_fields=['role', 'is_active'])
    return user
