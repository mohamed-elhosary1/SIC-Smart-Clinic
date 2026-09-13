from datetime import datetime, timedelta
import reflex as rx

from main import (
    ClinicManager,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
    User,
    StaffUser,
    DoctorUser,
    authenticate,
    USERS_DB,
    ClinicError,
    DuplicateBookingError,
    InvalidAppointmentTimeError,
    PatientNotFoundError,
    DoctorNotFoundError,
    InvalidFormatError,
    validate_patient_id,
    validate_doctor_id,
    validate_phone,
)

# Shared domain controller singleton
clinic_manager = ClinicManager(base_fee=100.0)
clinic_manager.load_from_file("clinic_data.json")


class State(rx.State):
    """Central reactive web application state bridging Reflex to ClinicManager."""

    # Session & Authentication
    auth_role: str = ""  # 'staff', 'doctor', 'patient', ''
    auth_username: str = ""
    auth_display_name: str = ""
    auth_doctor_id: str = ""
    auth_patient_id: str = ""
    login_username_input: str = ""
    login_password_input: str = ""
    patient_lookup_input: str = ""
    login_error_msg: str = ""
    landing_mode: str = ""  # '', 'patient', 'admin'

    def set_landing_mode(self, mode: str):
        self.landing_mode = mode
        self.login_error_msg = ""

    def go_back_to_landing(self):
        self.landing_mode = ""
        self.login_error_msg = ""

    def set_staff_demo_creds(self):
        self.login_username_input = "staff"
        self.login_password_input = "staff123"

    def set_doctor_demo_creds(self):
        self.login_username_input = "doctor"
        self.login_password_input = "doc123"

    # Staff Navigation
    staff_active_tab: str = "dashboard"  # 'dashboard', 'queue', 'patients', 'doctors', 'reports', 'admin'

    # Queue & Appointment Filters
    queue_search_query: str = ""
    queue_priority_filter: str = "All Priorities"
    queue_status_filter: str = "All Statuses"
    queue_doctor_filter: str = "All Doctors"

    # Patient Search
    patient_search_query: str = ""

    # Booking Dialog
    booking_modal_open: bool = False
    booking_patient_id: str = ""
    booking_doctor_id: str = ""
    booking_date_str: str = ""
    booking_time_str: str = ""
    booking_case_type: str = "Regular"
    booking_conflict_error: str = ""
    booking_has_conflict: bool = False

    # Patient Registration Dialog
    patient_modal_open: bool = False
    new_patient_name: str = ""
    new_patient_phone: str = ""
    new_patient_age: str = ""
    new_patient_case_type: str = ""
    new_patient_is_emergency: bool = False
    patient_error_msg: str = ""

    # Doctor Registration Dialog
    doctor_modal_open: bool = False
    new_doctor_name: str = ""
    new_doctor_phone: str = ""
    new_doctor_specialty: str = ""
    doctor_error_msg: str = ""

    # Medical History Dialog
    history_modal_open: bool = False
    history_patient_id: str = ""
    history_patient_name: str = ""
    history_visits: list[dict] = []
    history_is_cache_hit: bool = False

    # Confirmation Dialog
    confirm_modal_open: bool = False
    confirm_title: str = ""
    confirm_message: str = ""
    confirm_action_type: str = ""
    confirm_target_index: int = -1

    # Doctor Portal
    doctor_status: str = "AVAILABLE"
    doctor_queue_filter: str = "my"  # 'my', 'all'
    doctor_notes_input: str = ""

    # Patient Portal Simulation & State
    patient_stage_sim: str = "waiting"  # 'waiting', 'consulting', 'completed'

    # Core Reactive Data Collections (Serialized for Reflex Frontend)
    patients_list: list[dict] = []
    doctors_list: list[dict] = []
    appointments_list: list[dict] = []
    kpi_metrics: dict = {}
    daily_report_metrics: dict = {}
    daily_report_table_text: str = ""

    # -------------------------------------------------------------
    # Initialization & Synchronization
    # -------------------------------------------------------------

    def on_load(self):
        """Triggered when the application or page loads."""
        self.refresh_data()
        if not self.booking_date_str:
            now = datetime.now()
            self.booking_date_str = now.strftime("%Y-%m-%d")
            minutes = 30 if now.minute < 30 else 0
            hour = now.hour if now.minute < 30 else (now.hour + 1) % 24
            self.booking_time_str = f"{hour:02d}:{minutes:02d}"

    def refresh_data(self):
        """Pull domain data from clinic_manager and update reactive collections."""
        # 1. Patients
        p_list = []
        for p in clinic_manager.patients.values():
            initials = "".join([w[0].upper() for w in p.name.split()[:2]]) if p.name else "PT"
            p_list.append({
                "person_id": p.person_id,
                "name": p.name,
                "phone": p.phone,
                "age": p.age,
                "case_type": p.case_type or "General Checkup",
                "priority_level": p.priority_level(),
                "priority_str": "EMERGENCY" if p.priority_level() == 1 else "REGULAR",
                "initials": initials,
            })
        self.patients_list = p_list

        # 2. Doctors
        d_list = []
        for d in clinic_manager.doctors.values():
            initials = "".join([w[0].upper() for w in d.name.split()[:2]]) if d.name else "DR"
            d_list.append({
                "person_id": d.person_id,
                "name": d.name,
                "phone": d.phone,
                "specialty": d.specialty,
                "availability": d.availability,
                "status_str": "AVAILABLE" if d.availability else "BUSY",
                "initials": initials,
            })
        self.doctors_list = d_list

        # 3. Appointments
        a_list = []
        for idx, a in enumerate(clinic_manager.appointments):
            t_str = a.time.strftime("%I:%M %p") if isinstance(a.time, datetime) else str(a.time)
            end_t = (a.time + a.duration).strftime("%I:%M %p") if isinstance(a.time, datetime) else ""
            slot_str = f"{t_str} - {end_t}" if end_t else t_str
            date_str = a.time.strftime("%Y-%m-%d") if isinstance(a.time, datetime) else ""
            p_initials = "".join([w[0].upper() for w in a.patient.name.split()[:2]]) if a.patient.name else "PT"
            a_list.append({
                "index": idx,
                "patient_id": a.patient.person_id,
                "patient_name": a.patient.name,
                "patient_initials": p_initials,
                "doctor_id": a.doctor.person_id,
                "doctor_name": a.doctor.name,
                "doctor_specialty": a.doctor.specialty,
                "time_str": t_str,
                "end_time_str": end_t,
                "slot_str": slot_str,
                "date_str": date_str,
                "status": a.status,
                "status_str": a.status.upper().replace("_", " "),
                "fee": a.fee,
                "fee_str": f"${a.fee:.2f}",
                "priority_level": a.patient.priority_level(),
                "priority_str": "EMERGENCY" if a.patient.priority_level() == 1 else "REGULAR",
                "case_type": a.patient.case_type or "General Care",
            })
        self.appointments_list = a_list

        # 4. KPI Metrics
        tot_patients = len(clinic_manager.patients)
        reg_patients = sum(1 for p in clinic_manager.patients.values() if p.priority_level() != 1)
        emg_patients = sum(1 for p in clinic_manager.patients.values() if p.priority_level() == 1)

        tot_docs = len(clinic_manager.doctors)
        act_docs = sum(1 for d in clinic_manager.doctors.values() if d.availability)
        bsy_docs = tot_docs - act_docs

        waiting = sum(1 for a in clinic_manager.appointments if a.status == "pending")
        in_prog = sum(1 for a in clinic_manager.appointments if a.status == "in_progress")
        completed = sum(1 for a in clinic_manager.appointments if a.status == "completed")
        rev = clinic_manager.calculate_total_revenue()

        self.kpi_metrics = {
            "total_patients": tot_patients,
            "regular_patients": reg_patients,
            "emergency_patients": emg_patients,
            "total_doctors": tot_docs,
            "active_doctors": act_docs,
            "active_doctors_str": f"{act_docs} active on duty",
            "busy_doctors": bsy_docs,
            "waiting_queue": waiting,
            "in_consultation": in_prog,
            "completed_today": completed,
            "revenue_today": rev,
            "revenue_today_str": f"${rev:,.2f}",
        }

        # 5. Reports
        rep = clinic_manager._compute_report_metrics()
        self.daily_report_metrics = rep
        self.daily_report_table_text = clinic_manager._format_report_table(rep, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # -------------------------------------------------------------
    # Computed Properties (@rx.var)
    # -------------------------------------------------------------

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self.auth_role)

    @rx.var
    def is_staff(self) -> bool:
        return self.auth_role == "staff"

    @rx.var
    def is_doctor(self) -> bool:
        return self.auth_role == "doctor"

    @rx.var
    def is_patient(self) -> bool:
        return self.auth_role == "patient"

    @rx.var
    def filtered_appointments(self) -> list[dict]:
        res = list(self.appointments_list)
        # Search query
        if self.queue_search_query:
            q = self.queue_search_query.strip().lower()
            res = [
                a for a in res
                if q in a["patient_name"].lower() or q in a["patient_id"].lower() or q in a["doctor_name"].lower()
            ]
        # Priority filter
        if self.queue_priority_filter == "Emergency":
            res = [a for a in res if a["priority_level"] == 1]
        elif self.queue_priority_filter == "Regular":
            res = [a for a in res if a["priority_level"] != 1]
        # Status filter
        if self.queue_status_filter in ("Waiting", "pending"):
            res = [a for a in res if a["status"] == "pending"]
        elif self.queue_status_filter in ("In Consultation", "in_progress"):
            res = [a for a in res if a["status"] == "in_progress"]
        elif self.queue_status_filter in ("Completed", "completed"):
            res = [a for a in res if a["status"] == "completed"]
        elif self.queue_status_filter in ("Cancelled", "cancelled"):
            res = [a for a in res if a["status"] == "cancelled"]
        # Doctor filter
        if self.queue_doctor_filter != "All Doctors":
            res = [a for a in res if self.queue_doctor_filter.lower() in a["doctor_name"].lower()]
        return res

    @rx.var
    def live_waiting_queue(self) -> list[dict]:
        """Priority-sorted waiting queue (Emergency first, then appointment time)."""
        waiting = [a for a in self.appointments_list if a["status"] == "pending"]
        waiting.sort(key=lambda x: (x["priority_level"], x["slot_str"]))
        return waiting

    @rx.var
    def filtered_patients(self) -> list[dict]:
        if not self.patient_search_query:
            return self.patients_list
        q = self.patient_search_query.strip().lower()
        return [
            p for p in self.patients_list
            if q in p["name"].lower() or q in p["person_id"].lower() or q in p["phone"]
        ]

    @rx.var
    def doctor_profile(self) -> dict:
        """Logged in doctor profile."""
        if not self.auth_doctor_id:
            if self.doctors_list:
                return self.doctors_list[0]
            return {"person_id": "doctor-1", "name": "Clinician", "specialty": "General Practice", "availability": True}
        for d in self.doctors_list:
            if d["person_id"] == self.auth_doctor_id:
                return d
        return {"person_id": self.auth_doctor_id, "name": self.auth_display_name, "specialty": "Internal Medicine", "availability": True}

    @rx.var
    def doctor_queue(self) -> list[dict]:
        """Queue filtered for doctor view."""
        doc = self.doctor_profile
        doc_id = doc.get("person_id", "")
        if self.doctor_queue_filter == "my" and doc_id:
            return [a for a in self.appointments_list if a["doctor_id"] == doc_id]
        return self.appointments_list

    @rx.var
    def doctor_active_consultation(self) -> dict:
        """Find first in_progress appointment for logged-in doctor."""
        doc_id = self.doctor_profile.get("person_id", "")
        for a in self.appointments_list:
            if a["status"] == "in_progress" and (not doc_id or a["doctor_id"] == doc_id):
                return a
        # Fallback to first waiting patient if no active consultation
        for a in self.live_waiting_queue:
            if not doc_id or a["doctor_id"] == doc_id:
                return a
        if self.appointments_list:
            return self.appointments_list[0]
        return {}

    @rx.var
    def patient_profile(self) -> dict:
        """Profile of logged-in patient."""
        if not self.auth_patient_id:
            if self.patients_list:
                return self.patients_list[0]
            return {"person_id": "patient-101", "name": "Patient", "phone": "01000000000", "case_type": "General Checkup", "age": 25}
        for p in self.patients_list:
            if p["person_id"] == self.auth_patient_id:
                return p
        return {"person_id": self.auth_patient_id, "name": "Patient", "phone": "", "case_type": "", "age": 25}

    @rx.var
    def patient_appointments(self) -> list[dict]:
        p_id = self.patient_profile.get("person_id", "")
        return [a for a in self.appointments_list if a["patient_id"] == p_id]

    @rx.var
    def patient_queue_ticket(self) -> dict:
        """Live queue ticket calculation for current patient."""
        p_id = self.patient_profile.get("person_id", "")
        waiting_q = self.live_waiting_queue
        position = 0
        total_waiting = len(waiting_q)
        current_appt = None

        for idx, a in enumerate(waiting_q):
            if a["patient_id"] == p_id:
                position = idx + 1
                current_appt = a
                break

        in_prog = [a for a in self.appointments_list if a["patient_id"] == p_id and a["status"] == "in_progress"]
        if in_prog:
            active = in_prog[0]
            return {
                "position": 0,
                "position_str": "NOW",
                "queue_headline": "Your consultation is currently in progress",
                "total_waiting": total_waiting,
                "doctor_name": active["doctor_name"],
                "doctor_display": f"Dr. {active['doctor_name']}",
                "doctor_specialty": active["doctor_specialty"],
                "slot_str": active["slot_str"],
                "status": "consulting",
                "status_str": "IN CONSULTATION",
                "estimated_call": "NOW",
                "mins_remaining": 0,
            }

        if position > 0 and current_appt:
            mins_rem = position * 15
            est_time = (datetime.now() + timedelta(minutes=mins_rem)).strftime("%I:%M %p")
            return {
                "position": position,
                "position_str": f"#{position}",
                "queue_headline": f"You are #{position} in line",
                "total_waiting": total_waiting,
                "doctor_name": current_appt["doctor_name"],
                "doctor_display": f"Dr. {current_appt['doctor_name']}",
                "doctor_specialty": current_appt["doctor_specialty"],
                "slot_str": current_appt["slot_str"],
                "status": "waiting",
                "status_str": "WAITING IN QUEUE",
                "estimated_call": est_time,
                "mins_remaining": mins_rem,
            }

        completed = [a for a in self.appointments_list if a["patient_id"] == p_id and a["status"] == "completed"]
        if completed:
            last = completed[-1]
            return {
                "position": 0,
                "position_str": "DONE",
                "queue_headline": "All scheduled visits completed today",
                "total_waiting": total_waiting,
                "doctor_name": last["doctor_name"],
                "doctor_display": f"Dr. {last['doctor_name']}",
                "doctor_specialty": last["doctor_specialty"],
                "slot_str": last["slot_str"],
                "status": "completed",
                "status_str": "VISIT COMPLETED",
                "estimated_call": "Completed",
                "mins_remaining": 0,
            }

        return {
            "position": 0,
            "position_str": "--",
            "queue_headline": "No active waiting queue position",
            "total_waiting": total_waiting,
            "doctor_name": "No active booking",
            "doctor_display": "No attending physician assigned",
            "doctor_specialty": "Reception",
            "slot_str": "None scheduled",
            "status": "none",
            "status_str": "NO ACTIVE QUEUE",
            "estimated_call": "--",
            "mins_remaining": 0,
        }

    # -------------------------------------------------------------
    # Authentication Actions
    # -------------------------------------------------------------

    def set_login_username(self, val: str):
        self.login_username_input = val

    def set_login_password(self, val: str):
        self.login_password_input = val

    def set_patient_lookup(self, val: str):
        self.patient_lookup_input = val

    def login_staff_or_doctor(self):
        """Authenticate against USERS_DB via main.py authenticate()."""
        u = self.login_username_input.strip()
        p = self.login_password_input.strip()
        if not u or not p:
            self.login_error_msg = "Please enter both username and password."
            return rx.toast.error(self.login_error_msg)

        try:
            user = authenticate(u, p)
            clinic_manager.set_current_user(user)
            self.auth_username = user.username
            self.login_error_msg = ""

            if isinstance(user, StaffUser):
                self.auth_role = "staff"
                self.auth_display_name = "Clinic Administrator"
                self.refresh_data()
                return rx.redirect("/staff")
            elif isinstance(user, DoctorUser):
                self.auth_role = "doctor"
                doc_entity = None
                for d in clinic_manager.doctors.values():
                    if u.lower() in d.name.lower() or u.lower() in d.person_id.lower():
                        doc_entity = d
                        break
                if doc_entity:
                    self.auth_doctor_id = doc_entity.person_id
                    self.auth_display_name = f"Dr. {doc_entity.name}"
                else:
                    self.auth_doctor_id = list(clinic_manager.doctors.keys())[0] if clinic_manager.doctors else ""
                    self.auth_display_name = f"Dr. {self.auth_username}"
                self.refresh_data()
                return rx.redirect("/doctor")
        except ClinicError as err:
            self.login_error_msg = str(err)
            return rx.toast.error(f"Login failed: {err}")

    def login_patient(self):
        """Passwordless Patient lookup by ID (e.g. patient-101)."""
        p_id = self.patient_lookup_input.strip()
        if not p_id:
            self.login_error_msg = "Please enter your Patient ID (e.g. patient-101)."
            return rx.toast.error(self.login_error_msg)

        if p_id not in clinic_manager.patients:
            self.login_error_msg = f"Patient ID '{p_id}' not found. Please check your ID."
            return rx.toast.error(self.login_error_msg)

        patient = clinic_manager.patients[p_id]
        self.auth_role = "patient"
        self.auth_patient_id = patient.person_id
        self.auth_display_name = patient.name
        self.login_error_msg = ""
        self.refresh_data()
        return rx.redirect("/patient")

    def select_demo_patient(self, p_id: str):
        self.patient_lookup_input = p_id
        return self.login_patient()

    def logout(self):
        """Clear active session and return to login page."""
        clinic_manager.set_current_user(None)
        clinic_manager.save_to_file("clinic_data.json", silent=True)
        self.auth_role = ""
        self.auth_username = ""
        self.auth_display_name = ""
        self.auth_doctor_id = ""
        self.auth_patient_id = ""
        self.login_username_input = ""
        self.login_password_input = ""
        self.patient_lookup_input = ""
        self.login_error_msg = ""
        return rx.redirect("/")

    # -------------------------------------------------------------
    # Navigation & Filtering Controls
    # -------------------------------------------------------------

    def set_staff_tab(self, tab: str):
        self.staff_active_tab = tab

    def set_queue_search(self, q: str):
        self.queue_search_query = q

    def set_queue_priority(self, p: str):
        self.queue_priority_filter = p

    def set_queue_status(self, s: str):
        self.queue_status_filter = s

    def set_queue_doctor(self, d: str):
        self.queue_doctor_filter = d

    def set_patient_search(self, q: str):
        self.patient_search_query = q

    def set_doctor_queue_filter(self, f: str | list[str]):
        self.doctor_queue_filter = f if isinstance(f, str) else (f[0] if f else "my")

    def set_patient_stage_sim(self, st: str | list[str]):
        self.patient_stage_sim = st if isinstance(st, str) else (st[0] if st else "waiting")

    # -------------------------------------------------------------
    # Appointment Booking & Conflict Handling
    # -------------------------------------------------------------

    def open_booking_modal(self):
        self.booking_modal_open = True
        self.booking_conflict_error = ""
        self.booking_has_conflict = False
        if not self.booking_patient_id and self.patients_list:
            self.booking_patient_id = self.patients_list[0]["person_id"]
        if not self.booking_doctor_id and self.doctors_list:
            self.booking_doctor_id = self.doctors_list[0]["person_id"]
        if not self.booking_date_str:
            self.booking_date_str = datetime.now().strftime("%Y-%m-%d")
        if not self.booking_time_str:
            self.booking_time_str = "11:00"

    def close_booking_modal(self):
        self.booking_modal_open = False
        self.booking_conflict_error = ""
        self.booking_has_conflict = False

    def set_booking_patient(self, p_id: str):
        self.booking_patient_id = p_id
        self.validate_booking_slot()

    def set_booking_doctor(self, d_id: str):
        self.booking_doctor_id = d_id
        self.validate_booking_slot()

    def set_booking_date(self, d_str: str):
        self.booking_date_str = d_str
        self.validate_booking_slot()

    def set_booking_time(self, t_str: str):
        self.booking_time_str = t_str
        self.validate_booking_slot()

    def set_booking_case_type(self, c_type: str):
        self.booking_case_type = c_type

    def validate_booking_slot(self):
        """Pre-validate proposed slot against existing 30-minute appointments."""
        if not self.booking_doctor_id or not self.booking_date_str or not self.booking_time_str:
            return

        date_time_str = f"{self.booking_date_str} {self.booking_time_str}"
        try:
            target_dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return

        # Check doctor collision
        for existing in clinic_manager.appointments:
            if existing.doctor.person_id == self.booking_doctor_id and existing.status != "cancelled":
                if existing.overlaps_with(target_dt, timedelta(minutes=30)):
                    doc_name = existing.doctor.name
                    t_start = existing.time.strftime("%I:%M %p")
                    t_end = (existing.time + existing.duration).strftime("%I:%M %p")
                    self.booking_has_conflict = True
                    self.booking_conflict_error = (
                        f"Dr. {doc_name} already has an appointment during this 30-minute slot "
                        f"({existing.patient.name} at {t_start} - {t_end}). Please select an alternate time slot."
                    )
                    return

        # Check patient collision
        if self.booking_patient_id:
            for existing in clinic_manager.appointments:
                if existing.patient.person_id == self.booking_patient_id and existing.status != "cancelled":
                    if existing.overlaps_with(target_dt, timedelta(minutes=30)):
                        t_start = existing.time.strftime("%I:%M %p")
                        t_end = (existing.time + existing.duration).strftime("%I:%M %p")
                        self.booking_has_conflict = True
                        self.booking_conflict_error = (
                            f"Patient {existing.patient.name} already has an appointment scheduled between "
                            f"{t_start} and {t_end}. Please choose another slot."
                        )
                        return

        self.booking_has_conflict = False
        self.booking_conflict_error = ""

    def confirm_book_appointment(self):
        """Call clinic_manager.book_appointment() with RBAC enforcement and auto-save."""
        if not self.booking_patient_id:
            return rx.toast.error("Please select a patient.")
        if not self.booking_doctor_id:
            return rx.toast.error("Please select an attending doctor.")
        if not self.booking_date_str or not self.booking_time_str:
            return rx.toast.error("Please provide a valid date and time.")

        slot_str = f"{self.booking_date_str} {self.booking_time_str}"

        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("book_appointment"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))

        try:
            appt = clinic_manager.book_appointment(
                patient_id=self.booking_patient_id,
                doctor_id=self.booking_doctor_id,
                time=slot_str,
            )
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            self.booking_modal_open = False
            self.booking_conflict_error = ""
            self.booking_has_conflict = False
            return rx.toast.success(f"Appointment booked for {appt.patient.name} with Dr. {appt.doctor.name}!")
        except DuplicateBookingError as dup_err:
            self.booking_has_conflict = True
            self.booking_conflict_error = str(dup_err)
            return rx.toast.error(f"Conflict: {dup_err}")
        except ClinicError as err:
            return rx.toast.error(f"Booking failed: {err}")
        except Exception as e:
            return rx.toast.error(f"Error: {e}")

    # -------------------------------------------------------------
    # Appointment Workflow Actions
    # -------------------------------------------------------------

    def start_consultation(self, appt_index: int):
        """Transition appointment status to 'in_progress'."""
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("update_visit_status"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))
        try:
            clinic_manager.update_visit_status(appt_index, "in_progress")
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            return rx.toast.info("Consultation started: patient status updated to In Progress.")
        except Exception as e:
            return rx.toast.error(f"Could not start consultation: {e}")

    def complete_consultation(self, appt_index: int):
        """Transition appointment status to 'completed' and record visit."""
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("update_visit_status"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))
        try:
            clinic_manager.update_visit_status(appt_index, "completed")
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            return rx.toast.success("Consultation successfully concluded and billed!")
        except Exception as e:
            return rx.toast.error(f"Could not complete consultation: {e}")

    def cancel_appointment(self, appt_index: int):
        """Cancel appointment and release the 30-minute busy duration window."""
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("update_visit_status"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))
        try:
            clinic_manager.update_visit_status(appt_index, "cancelled")
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            return rx.toast.warning("Appointment cancelled and 30-minute slot released.")
        except Exception as e:
            return rx.toast.error(f"Could not cancel appointment: {e}")

    def prompt_delete_appointment(self, appt_index: int):
        if appt_index < 0 or appt_index >= len(clinic_manager.appointments):
            return
        appt = clinic_manager.appointments[appt_index]
        self.confirm_title = "Delete Appointment"
        self.confirm_message = f"Are you sure you want to permanently remove the appointment for {appt.patient.name}? This will free the reserved slot."
        self.confirm_action_type = "delete_appointment"
        self.confirm_target_index = appt_index
        self.confirm_modal_open = True

    def execute_confirm_action(self):
        if self.confirm_action_type == "delete_appointment":
            if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("delete_appointment"):
                clinic_manager.set_current_user(StaffUser("staff", "staff123"))
            try:
                clinic_manager.delete_appointment(self.confirm_target_index)
                clinic_manager.save_to_file("clinic_data.json", silent=True)
                self.refresh_data()
                self.confirm_modal_open = False
                return rx.toast.success("Appointment permanently removed.")
            except Exception as e:
                self.confirm_modal_open = False
                return rx.toast.error(f"Delete failed: {e}")
        elif self.confirm_action_type == "reset_database":
            if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("reset_database"):
                clinic_manager.set_current_user(StaffUser("staff", "staff123"))
            try:
                clinic_manager.reset_database("clinic_data.json")
                self.refresh_data()
                self.confirm_modal_open = False
                return rx.toast.warning("Clinic database has been completely reset.")
            except Exception as e:
                self.confirm_modal_open = False
                return rx.toast.error(f"Reset failed: {e}")

    def close_confirm_modal(self):
        self.confirm_modal_open = False

    # -------------------------------------------------------------
    # Patient Registration
    # -------------------------------------------------------------

    def open_patient_modal(self):
        self.patient_modal_open = True
        self.new_patient_name = ""
        self.new_patient_phone = ""
        self.new_patient_age = ""
        self.new_patient_case_type = ""
        self.new_patient_is_emergency = False
        self.patient_error_msg = ""

    def close_patient_modal(self):
        self.patient_modal_open = False
        self.patient_error_msg = ""

    def set_new_patient_name(self, val: str):
        self.new_patient_name = val

    def set_new_patient_phone(self, val: str):
        self.new_patient_phone = val

    def set_new_patient_age(self, val: str):
        self.new_patient_age = val

    def set_new_patient_case_type(self, val: str):
        self.new_patient_case_type = val

    def set_new_patient_is_emergency(self, val: bool):
        self.new_patient_is_emergency = val

    def confirm_register_patient(self):
        name = self.new_patient_name.strip()
        phone = self.new_patient_phone.strip()
        age_str = self.new_patient_age.strip()
        case_type = self.new_patient_case_type.strip()

        if not name or not phone or not age_str:
            self.patient_error_msg = "Name, phone, and age are required."
            return rx.toast.error(self.patient_error_msg)

        try:
            age = int(age_str)
            if age <= 0 or age > 130:
                raise ValueError
        except ValueError:
            self.patient_error_msg = "Please enter a valid age between 1 and 130."
            return rx.toast.error(self.patient_error_msg)

        if not validate_phone(phone):
            self.patient_error_msg = "Invalid Egyptian phone format. Expected 11 digits starting with '01' (e.g. 01012345678)."
            return rx.toast.error(self.patient_error_msg)

        p_id = clinic_manager.generate_unique_patient_id()

        if self.new_patient_is_emergency:
            pat = EmergencyPatient(person_id=p_id, name=name, phone=phone, age=age, case_type=case_type)
        else:
            pat = RegularPatient(person_id=p_id, name=name, phone=phone, age=age, case_type=case_type)

        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("register_patient"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))

        try:
            clinic_manager.register_patient(pat)
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            self.patient_modal_open = False
            return rx.toast.success(f"Patient {pat.name} registered successfully with ID {pat.person_id}!")
        except Exception as e:
            self.patient_error_msg = str(e)
            return rx.toast.error(f"Registration failed: {e}")

    # -------------------------------------------------------------
    # Doctor Registration & Availability
    # -------------------------------------------------------------

    def open_doctor_modal(self):
        self.doctor_modal_open = True
        self.new_doctor_name = ""
        self.new_doctor_phone = ""
        self.new_doctor_specialty = ""
        self.doctor_error_msg = ""

    def close_doctor_modal(self):
        self.doctor_modal_open = False
        self.doctor_error_msg = ""

    def set_new_doctor_name(self, val: str):
        self.new_doctor_name = val

    def set_new_doctor_phone(self, val: str):
        self.new_doctor_phone = val

    def set_new_doctor_specialty(self, val: str):
        self.new_doctor_specialty = val

    def confirm_add_doctor(self):
        name = self.new_doctor_name.strip()
        phone = self.new_doctor_phone.strip()
        spec = self.new_doctor_specialty.strip()

        if not name or not phone or not spec:
            self.doctor_error_msg = "Name, phone, and specialty are required."
            return rx.toast.error(self.doctor_error_msg)

        if not validate_phone(phone):
            self.doctor_error_msg = "Invalid Egyptian phone format (11 digits starting with 01)."
            return rx.toast.error(self.doctor_error_msg)

        doc_id = clinic_manager.generate_unique_doctor_id()
        doc = Doctor(person_id=doc_id, name=name, phone=phone, specialty=spec, availability=True)

        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("add_doctor"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))

        try:
            clinic_manager.add_doctor(doc)
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            self.doctor_modal_open = False
            return rx.toast.success(f"Dr. {doc.name} successfully registered with ID {doc.person_id}!")
        except Exception as e:
            self.doctor_error_msg = str(e)
            return rx.toast.error(f"Add doctor failed: {e}")

    def toggle_doctor_availability(self, doctor_id: str):
        """Toggle doctor's availability using domain controller."""
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("toggle_doctor_availability"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))
        try:
            status = clinic_manager.toggle_doctor_availability(doctor_id)
            clinic_manager.save_to_file("clinic_data.json", silent=True)
            self.refresh_data()
            status_text = "Available" if status else "Unavailable (Busy)"
            return rx.toast.info(f"Doctor status changed to {status_text}.")
        except Exception as e:
            return rx.toast.error(f"Could not toggle status: {e}")

    # -------------------------------------------------------------
    # Medical History Inspection (Memoization Cache)
    # -------------------------------------------------------------

    def inspect_patient_history(self, patient_id: str):
        if patient_id not in clinic_manager.patients:
            return rx.toast.error(f"Patient {patient_id} not found.")

        pat = clinic_manager.patients[patient_id]
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("view_patient_history"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))

        try:
            visits, is_hit = clinic_manager.get_patient_completed_visits(patient_id, return_status=True)
            v_list = []
            for v in visits:
                d_str = v.time.strftime("%Y-%m-%d %I:%M %p") if isinstance(v.time, datetime) else str(v.time)
                v_list.append({
                    "date_str": d_str,
                    "doctor_name": v.doctor.name,
                    "specialty": v.doctor.specialty,
                    "fee_str": f"${v.fee:.2f}",
                    "case_type": getattr(v.patient, "case_type", "Routine Consultation"),
                    "status": v.status.upper(),
                })
            self.history_patient_id = pat.person_id
            self.history_patient_name = pat.name
            self.history_visits = v_list
            self.history_is_cache_hit = is_hit
            self.history_modal_open = True
        except Exception as e:
            return rx.toast.error(f"Failed retrieving history: {e}")

    def close_history_modal(self):
        self.history_modal_open = False

    # -------------------------------------------------------------
    # Administration & File I/O
    # -------------------------------------------------------------

    def export_daily_report(self):
        """Export daily report to daily_report.txt via domain method."""
        if clinic_manager.current_user is None or not clinic_manager.current_user.has_permission("export_report"):
            clinic_manager.set_current_user(StaffUser("staff", "staff123"))
        success = clinic_manager.export_report_to_file("daily_report.txt")
        if success:
            return rx.toast.success("Daily report successfully exported to 'daily_report.txt'!")
        else:
            return rx.toast.error("Failed exporting report to file.")

    def save_database(self):
        success = clinic_manager.save_to_file("clinic_data.json")
        if success:
            self.refresh_data()
            return rx.toast.success("All clinic data saved successfully to 'clinic_data.json'!")
        return rx.toast.error("Failed saving database to file.")

    def reload_database(self):
        success = clinic_manager.load_from_file("clinic_data.json")
        if success:
            self.refresh_data()
            return rx.toast.info("Database reloaded from 'clinic_data.json'.")
        return rx.toast.error("Failed reloading database from file.")

    def prompt_reset_database(self):
        self.confirm_title = "Reset Clinic Database"
        self.confirm_message = "WARNING: This will permanently wipe all registered patients, doctors, and appointments from clinic_data.json. Are you sure?"
        self.confirm_action_type = "reset_database"
        self.confirm_target_index = -1
        self.confirm_modal_open = True
