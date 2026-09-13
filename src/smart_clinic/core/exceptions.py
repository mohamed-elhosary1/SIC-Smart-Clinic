"""Custom domain exceptions for Smart Clinic Queue System."""


class ClinicError(Exception):
    """Base exception for all domain-specific errors in Smart Clinic."""
    pass


class InvalidAppointmentTimeError(ClinicError):
    """Raised when appointment format, hours, or time ordering is invalid."""
    pass


class DuplicateBookingError(ClinicError):
    """Raised when a patient or doctor already has an overlapping appointment slot."""
    pass


class PatientNotFoundError(ClinicError):
    """Raised when a requested patient ID does not exist in records."""
    pass


class DoctorNotFoundError(ClinicError):
    """Raised when a requested doctor ID does not exist in records."""
    pass


class InvalidFormatError(ClinicError):
    """Raised when user input fails pattern or semantic validation."""
    pass
