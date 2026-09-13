"""Authentication and Role-Based Access Control (RBAC)."""

from typing import Callable, Dict, Set
from .exceptions import ClinicError


class User:
    """Base class for authenticated system users (Staff / Doctor)."""

    def __init__(self, username: str, password: str, allowed_actions: Set[str]):
        self.username = username
        self.password = password
        self.allowed_actions = allowed_actions

    def has_permission(self, action: str) -> bool:
        """Check whether user has permission for a specific action."""
        return action in self.allowed_actions

    def display_role(self) -> str:
        """Return the display role name."""
        return "Generic User"


class StaffUser(User):
    """Clinic staff member with full operational and administrative privileges."""

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=set())

    def has_permission(self, action: str) -> bool:
        return True

    def display_role(self) -> str:
        return "Staff"


class DoctorUser(User):
    """Medical doctor with scoped clinical permissions."""

    DOCTOR_ACTIONS = {
        "view_queue",
        "update_visit_status",
        "daily_report",
        "view_history",
    }

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=self.DOCTOR_ACTIONS)

    def display_role(self) -> str:
        return "Doctor"


# Default credentials database for staff and doctors
USERS_DB: Dict[str, Dict] = {
    "staff": {
        "password": "staff123",
        "factory": lambda u, p: StaffUser(u, p),
    },
    "doctor": {
        "password": "doc123",
        "factory": lambda u, p: DoctorUser(u, p),
    },
}


def authenticate(username: str, password: str) -> User:
    """Authenticate administrative and medical staff against USERS_DB."""
    u_key = username.strip().lower()
    p_clean = password.strip()
    user_record = USERS_DB.get(u_key)
    if not user_record or user_record["password"] != p_clean:
        raise ClinicError("Invalid credentials. Please check username and password.")
    return user_record["factory"](username.strip(), p_clean)
