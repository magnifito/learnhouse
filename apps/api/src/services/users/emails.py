from pydantic import EmailStr
from src.db.organizations import OrganizationRead
from src.db.users import UserRead
from src.services.email.utils import send_email


def send_account_creation_email(
    user: UserRead,
    email: EmailStr,
):
    """
    Send account creation email.
    Returns True if sent successfully, False otherwise.
    Does not raise exceptions - allows user creation to proceed even if email fails.
    """
    # send email
    result = send_email(
        to=email,
        subject=f"Welcome to LearnHouse, {user.username}!",
        body=f"""
<html>
    <body>
        <p>Hello {user.username}</p>
        <p>Welcome to LearnHouse! , get started by creating your own organization or join a one.</p>
        <p>Need some help to get started ? <a href="https://university.learnhouse.io">LearnHouse Academy</a></p>
    </body>
</html>
""",
    )
    return result is not None


def send_password_reset_email(
    generated_reset_code: str,
    user: UserRead,
    organization: OrganizationRead,
    email: EmailStr,
):
    """
    Send password reset email.
    Returns True if sent successfully, False otherwise.
    """
    # send email
    result = send_email(
        to=email,
        subject="Reset your password",
        body=f"""
<html>
    <body>
        <p>Hello {user.username}</p>
        <p>You have requested to reset your password.</p>
        <p>Here is your reset code: {generated_reset_code}</p>
        <p>Click <a href="https://{organization.slug}.learnhouse.io/reset?orgslug={organization.slug}&email={email}&resetCode={generated_reset_code}">here</a> to reset your password.</p>
    </body>
</html>
""",
    )
    return result is not None
