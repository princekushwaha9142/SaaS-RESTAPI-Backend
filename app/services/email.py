import resend
from app.config import get_settings

settings = get_settings()


def _get_client():
    resend.api_key = settings.resend_api_key
    return resend


async def send_welcome_email(to_email: str, full_name: str) -> None:
    if not settings.resend_api_key:
        print("❌ RESEND_API_KEY missing!")
        return
    try:
        _get_client()
        result = resend.Emails.send({
            "from": settings.from_email,
            "to": [to_email],
            "subject": "Welcome to TaskManager!",
            "html": f"""
            <h2>Welcome, {full_name}! 🎉</h2>
            <p>Your account has been created successfully.</p>
            <p>You can now create projects, assign tasks, and collaborate!</p>
            <br>
            <p>Happy tasking!</p>
            """
        })
        print(f"✅ Welcome email sent: {result}")
    except Exception as e:
        print(f"❌ Email error: {e}")


async def send_task_assigned_email(
    to_email: str,
    full_name: str,
    task_title: str,
    project_name: str
) -> None:
    if not settings.resend_api_key:
        return
    try:
        _get_client()
        result = resend.Emails.send({
            "from": settings.from_email,
            "to": [to_email],
            "subject": f"Task Assigned: {task_title}",
            "html": f"""
            <h2>New Task Assigned! ✅</h2>
            <p>Hi {full_name},</p>
            <p>You have been assigned a new task:</p>
            <ul>
                <li><strong>Task:</strong> {task_title}</li>
                <li><strong>Project:</strong> {project_name}</li>
            </ul>
            <p>Login to view and update the task status.</p>
            """
        })
        print(f"✅ Task email sent: {result}")
    except Exception as e:
        print(f"❌ Task email error: {e}")


async def send_member_added_email(
    to_email: str,
    full_name: str,
    project_name: str,
    role: str
) -> None:
    if not settings.resend_api_key:
        return
    try:
        _get_client()
        result = resend.Emails.send({
            "from": settings.from_email,
            "to": [to_email],
            "subject": f"Added to Project: {project_name}",
            "html": f"""
            <h2>Project Invitation! 📁</h2>
            <p>Hi {full_name},</p>
            <p>You have been added to a project:</p>
            <ul>
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>Role:</strong> {role}</li>
            </ul>
            """
        })
        print(f"✅ Member email sent: {result}")
    except Exception as e:
        print(f"❌ Member email error: {e}")