# Smart Clinic Queue System

**Chapter 3 Capstone Project — Samsung Innovation Campus**  
**Project 5 — Smart Clinic Queue System**  
An enterprise-grade, single-file clinic queue management system featuring intelligent triage, 30-minute slot scheduling, role-based access control, memoized patient history, and automated JSON persistence with self-healing recovery.

---

## System Architecture

The project adheres strictly to a clean single-file runtime architecture:
* **[`main.py`](main.py)**: Contains the entire system implementation, including custom exception hierarchies, OOP domain models, regex validators, advanced functional tools (closures, custom iterators, recursion, memoization), role-based access control (RBAC), and interactive command-line interfaces.
* **[`clinic_data.json`](clinic_data.json)**: Permanent JSON database storage storing patients, doctors, and appointments with instant autosave and automatic `.bak` recovery.
* **[`ERD.md`](ERD.md)**: Comprehensive Entity-Relationship Diagram and OOP class diagram.
* **[`PROMPT_ROLE_REDESIGN.md`](PROMPT_ROLE_REDESIGN.md)**: Architectural specification detailing passwordless patient ID lookup and RBAC separation.

---

## Opening Screen & Role-Based Access Control (RBAC)

When launched, the system presents an intuitive, separated opening screen:

```text
+======================================================+
|                 SMART CLINIC SYSTEM                  |
|              Samsung Innovation Campus               |
+======================================================+
|  [1] Staff / Doctor Login                             |
|  [2] Patient Lookup (Enter your Patient ID)           |
|  [3] Exit                                             |
+------------------------------------------------------+
```

### System Accounts & Credentials

| Role | Username | Password | Operational Scope & Permissions |
|---|---|---|---|
| **Staff** | `staff` | `staff123` | Full administrative control: patient & doctor registration, appointment booking, status updates, deletion, daily reports, and database reset. |
| **Doctor** | `doctor` | `doc123` | Clinical operations: view prioritized waiting queue, update appointment consultation status, view daily statistics, and inspect patient medical history. |
| **Patient** | *N/A* (ID Lookup) | *No Password* | Passwordless patient portal: view scheduled appointments, real-time queue position, and completed visit history scoped strictly to the patient's ID. |

---

## 30-Minute Appointment Slot Scheduling & Conflict Prevention

The system enforces an intelligent **30-minute busy duration window** for all appointments:

1. **Fixed Duration Window**: Every appointment starting at time $T$ reserves a 30-minute time slot: $[T, T + 30\text{ minutes})$.
2. **Doctor Collision Guard**: A doctor cannot have overlapping appointments. Any attempt to book an appointment where $\max(T_1, T_2) < \min(T_1 + 30\text{m}, T_2 + 30\text{m})$ raises `DuplicateBookingError`.
3. **Patient Collision Guard**: A patient cannot be booked with two different doctors during overlapping intervals.
4. **Consecutive Booking Support**: Adjacent back-to-back bookings are fully supported (e.g., an appointment from `10:00 - 10:30` followed immediately by `10:30 - 11:00` does not collide).
5. **Slot Release upon Cancellation**: Cancelling or deleting an appointment automatically frees up its 30-minute slot for other patients.

---

## Role-Specific Menus

### 1. Staff Main Menu (13 Options)
- `[1] Register Patient`: Register new regular or emergency patient (auto-generates unique `patient-<num>`).
- `[2] Add Doctor`: Register doctor with medical specialty and availability.
- `[3] Book Appointment`: Schedule a 30-minute visit with conflict checking.
- `[4] Update Visit Status`: Transition status between Pending, In Progress, Completed, and Cancelled.
- `[5] Show Waiting Queue`: View real-time queue prioritized by triage level and appointment time.
- `[6] Toggle Doctor Status`: Switch doctor between Available and Unavailable.
- `[7] Delete Appointment`: Permanently remove appointment and release reserved slot.
- `[8] Daily Report`: Display unified clinic performance metrics and total revenue.
- `[9] Save Data Now`: Force immediate save to `clinic_data.json`.
- `[10] Reset Clinic Data`: Securely wipe clinic database with confirmation prompt.
- `[11] Export Report`: Export formatted daily report with timestamp to `daily_report.txt`.
- `[12] Patient History`: Inspect completed visit history with memoization cache tracking.
- `[13] Logout / Switch User`: Return to opening screen with automatic save.

### 2. Doctor Portal (5 Options)
- `[1] Show Waiting Queue`: Inspect prioritized queue.
- `[2] Update Visit Status`: Update consultation state.
- `[3] Daily Report`: View clinic daily report.
- `[4] Patient History`: Review patient medical history.
- `[5] Logout / Switch User`: Return to opening screen.

### 3. Patient Portal (Passwordless ID Lookup - 4 Options)
- `[1] My Appointments`: View all scheduled appointments for the patient.
- `[2] My Queue Position`: View live position in queue, assigned doctor, and total waiting patients.
- `[3] My Visit History`: Review completed visits with doctor and fee details.
- `[4] Back to Main Screen`: Return to opening screen.

---

## Class Hierarchy Summary

| Class | Type | Description |
|---|---|---|
| `Person` | Abstract Base Class | Shared attributes: `person_id`, `name`, `phone` with regex validation. |
| `Patient(Person)` | Domain Model | Extends `Person` with `age`, `case_type`, `visit_history`, and `priority_level()`. |
| `EmergencyPatient(Patient)` | Subclass | High-priority triage (`priority_level() == 1`), preempts queue. |
| `RegularPatient(Patient)` | Subclass | Standard priority (`priority_level() == 2`), regular queue order. |
| `Doctor(Person)` | Domain Model | Extends `Person` with `specialty`, `availability`, and `toggle_availability()`. |
| `Appointment` | Domain Model | Links Patient, Doctor, 30-minute slot window, status, and fee. |
| `WaitingQueueIterator` | Custom Iterator | Implements `__iter__` and `__next__` over sorted appointments. |
| `User` | Auth Base Class | Authenticated user model with `has_permission(action)`. |
| `StaffUser(User)` | Auth Subclass | Unrestricted permissions across all administrative operations. |
| `DoctorUser(User)` | Auth Subclass | Scoped clinical permissions (`view_queue`, `update_visit_status`, `daily_report`, `view_history`). |
| `ClinicManager` | Central Controller | Orchestrates business logic, triage closure, caching, and persistence. |

---

## Python Core Concepts Table

| Concept | Implementation in Code | Engineering Purpose & Value |
|---|---|---|
| **Closure & nonlocal** | `make_triage_calculator()` | Calculates fees and encapsulates an internal emergency counter state modified via `nonlocal`. |
| **Recursion (No Loops)** | `find_visits_recursive()` | Recursively traverses visit history to filter completed visits without any `for` or `while` loops. |
| **Memoization & Caching** | `ClinicManager.get_patient_completed_visits()` | Caches medical history queries in `_visit_lookup_cache` (`[CACHE HIT]` / `[COMPUTED]`) with automatic invalidation. |
| **Custom Iterator** | `WaitingQueueIterator` | Implements Python iterator protocol (`__iter__`, `__next__`, `StopIteration`) for sequential queue traversal. |
| **Lambda & Sorter** | `sort_queue_by_priority()` | Uses a composite lambda key `(priority, time)` to prioritize emergency cases before regular ones. |
| **Functional filter()** | `get_emergency_patients()` | Isolates emergency patients cleanly using functional `filter()`. |
| **Functional reduce()** | `calculate_total_revenue()` | Aggregates total clinic revenue from completed visits using `functools.reduce()`. |
| **Regex Precompilation** | `validate_patient_id()`, `validate_doctor_id()`, `validate_phone()` | Pre-compiled regex patterns validating IDs (`patient-\d+`, `doctor-\d+`) and 11-digit Egyptian mobile numbers (`01xxxxxxxxx`). |
| **Custom Exceptions** | `ClinicError`, `DuplicateBookingError`, `InvalidAppointmentTimeError`, ... | Clean exception hierarchy preventing application crashes and providing informative error feedback. |
| **Inheritance & Polymorphism** | `Person → Patient/Doctor`, `Emergency/Regular`, `User → Staff/Doctor` | True polymorphic dispatch across `display_profile()`, `priority_level()`, and `has_permission()`. |
| **DRY Reporting Engine** | `_compute_report_metrics()`, `_format_report_table()` | Shared calculation and formatting logic powering both console display and `daily_report.txt` export without code duplication. |
| **Self-Healing File I/O** | `save_to_file()`, `load_from_file()` | JSON database serialization with automatic directory creation, corrupt file backup (`.bak`), and graceful interruption autosave. |

---

## Direct Code Navigation Index

Click on any link below to jump directly to its exact line of implementation in [`main.py`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py):

### 1. System Constants & Exception Hierarchy
| Component / Class | Direct Code Link | Description |
|---|---|---|
| `DEFAULT_APPOINTMENT_DURATION` | [`main.py#L18`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L18) | Default 30-minute busy duration window (`timedelta(minutes=30)`). |
| `ClinicError` | [`main.py#L25`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L25) | Root exception for all clinic domain and validation errors. |
| `InvalidAppointmentTimeError` | [`main.py#L30`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L30) | Raised when appointment datetime format is invalid or scheduled in the past. |
| `DuplicateBookingError` | [`main.py#L35`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L35) | Raised when booking overlaps with an existing 30-min slot or on duplicate IDs. |
| `PatientNotFoundError` | [`main.py#L40`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L40) | Raised when requested patient ID is not found in the database. |
| `DoctorNotFoundError` | [`main.py#L45`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L45) | Raised when requested doctor ID is not found in the database. |
| `InvalidFormatError` | [`main.py#L50`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L50) | Raised when ID or phone number fails regex pattern validation. |

### 2. Authentication & Role-Based Access Control (RBAC)
| Component / Class | Direct Code Link | Description |
|---|---|---|
| `User` | [`main.py#L59`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L59) | Base class for authenticated users managing username and allowed permissions. |
| `StaffUser` | [`main.py#L76`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L76) | Staff user class returning `True` for all permission checks (full access). |
| `DoctorUser` | [`main.py#L90`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L90) | Doctor user class scoped to clinical actions (`view_queue`, `update_visit_status`, etc.). |
| `USERS_DB` | [`main.py#L108`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L108) | In-memory credentials dictionary storing default staff and doctor accounts. |
| `authenticate()` | [`main.py#L120`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L120) | Authenticates credentials against `USERS_DB` or raises `ClinicError`. |

### 3. Regex Validation & Input Normalizers
| Function | Direct Code Link | Description |
|---|---|---|
| `validate_patient_id()` | [`main.py#L139`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L139) | Precompiled regex validation for `patient-<number>`. |
| `validate_doctor_id()` | [`main.py#L144`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L144) | Precompiled regex validation for `doctor-<number>`. |
| `validate_phone()` | [`main.py#L149`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L149) | Precompiled regex validation for 11-digit Egyptian mobile numbers (`01xxxxxxxxx`). |
| `parse_patient_type()` | [`main.py#L158`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L158) | Normalizes patient category inputs (Regular / Emergency). |
| `parse_status()` | [`main.py#L168`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L168) | Normalizes visit state (Pending, In Progress, Completed, Cancelled). |
| `parse_menu_choice()` | [`main.py#L180`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L180) | Normalizes numeric and textual command-line menu inputs. |

### 4. Domain Models & OOP Core Classes
| Class / Property | Direct Code Link | Description |
|---|---|---|
| `Person` | [`main.py#L205`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L205) | Base entity storing person ID, validated phone number, and name. |
| `Patient` | [`main.py#L223`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L223) | Patient entity with age, diagnosis/case, and visit history. |
| `EmergencyPatient` | [`main.py#L246`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L246) | High-priority patient specialization returning `priority_level() == 1`. |
| `RegularPatient` | [`main.py#L256`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L256) | Normal priority patient specialization returning `priority_level() == 2`. |
| `Doctor` | [`main.py#L266`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L266) | Doctor entity with specialty and toggleable availability status. |
| `Appointment` | [`main.py#L285`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L285) | Appointment entity managing patient, doctor, fee, and 30-minute slot. |
| `Appointment.end_time` | [`main.py#L307`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L307) | Property calculating slot end time based on 30-minute duration. |
| `Appointment.overlaps_with()` | [`main.py#L311`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L311) | Interval collision detector: `max(T1, T2) < min(End1, End2)`. |

### 5. Advanced Python Constructs (Iterators, Closures, Recursion)
| Component | Direct Code Link | Description |
|---|---|---|
| `WaitingQueueIterator` | [`main.py#L338`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L338) | Custom iterator implementing `__iter__` and `__next__` over sorted queue. |
| `make_triage_calculator()` | [`main.py#L356`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L356) | Closure tracking emergency count via `nonlocal` with increment/decrement helpers. |
| `find_visits_recursive()` | [`main.py#L386`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L386) | Pure recursion filtering completed appointments without any loops. |

### 6. ClinicManager Core Logic & Persistence
| Method | Direct Code Link | Description |
|---|---|---|
| `ClinicManager` | [`main.py#L403`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L403) | Central controller managing database state, cache, and business operations. |
| `generate_unique_patient_id()` | [`main.py#L422`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L422) | Generates collision-free random patient ID (`patient-<1-1000>`). |
| `generate_unique_doctor_id()` | [`main.py#L430`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L430) | Generates collision-free random doctor ID (`doctor-<1-1000>`). |
| `register_patient()` | [`main.py#L440`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L440) | Registers a patient record and checks authorization. |
| `add_doctor()` | [`main.py#L450`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L450) | Registers a doctor record with initial availability. |
| `toggle_doctor_availability()` | [`main.py#L462`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L462) | Toggles doctor availability between available and busy. |
| `book_appointment()` | [`main.py#L475`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L475) | Books appointment with strict 30-minute busy window collision prevention. |
| `update_visit_status()` | [`main.py#L548`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L548) | Transitions appointment status with 30-minute reactivation safety guard. |
| `delete_appointment()` | [`main.py#L596`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L596) | Removes appointment and frees its reserved 30-minute slot. |
| `get_emergency_patients()` | [`main.py#L627`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L627) | Filters emergency cases using functional `filter()` and `lambda`. |
| `sort_queue_by_priority()` | [`main.py#L632`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L632) | Sorts waiting queue using composite `lambda (priority, time)`. |
| `calculate_total_revenue()` | [`main.py#L643`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L643) | Calculates revenue from completed visits using `functools.reduce()`. |
| `_compute_report_metrics()` | [`main.py#L650`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L650) | Aggregates daily clinic metrics into a DRY dictionary. |
| `_format_report_table()` | [`main.py#L672`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L672) | Formats report metrics into a fixed 56-character ASCII frame. |
| `daily_report()` | [`main.py#L710`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L710) | Generates and prints the daily clinic report table. |
| `export_report_to_file()` | [`main.py#L720`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L720) | Exports formatted report with timestamp to `daily_report.txt`. |
| `get_patient_completed_visits()` | [`main.py#L741`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L741) | Fetches completed visits with memoized caching (`[CACHE HIT]` / `[COMPUTED]`). |
| `save_to_file()` | [`main.py#L764`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L764) | Serializes clinic database to formatted JSON with directory creation. |
| `load_from_file()` | [`main.py#L813`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L813) | Deserializes database with auto-creation and `.bak` corrupt file recovery. |
| `reset_database()` | [`main.py#L941`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L941) | Wipes all database records and resets closure counters. |

### 7. Action Handlers & CLI Operations
| Action Handler | Direct Code Link | Description |
|---|---|---|
| `action_register_patient()` | [`main.py#L967`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L967) | Handles interactive patient registration and displays assigned ID card. |
| `action_add_doctor()` | [`main.py#L1045`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1045) | Handles interactive doctor onboarding with auto-ID option. |
| `action_book_appointment()` | [`main.py#L1099`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1099) | Guides staff through booking a 30-minute slot with conflict feedback. |
| `action_update_visit_status()` | [`main.py#L1171`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1171) | Interactively updates appointment state. |
| `action_show_queue()` | [`main.py#L1221`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1221) | Displays waiting queue table using `WaitingQueueIterator`. |
| `action_toggle_doctor_availability()` | [`main.py#L1255`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1255) | Interactively toggles doctor availability. |
| `action_delete_appointment()` | [`main.py#L1295`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1295) | Confirms and deletes appointment, releasing the reserved slot. |
| `action_daily_report()` | [`main.py#L1337`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1337) | Invokes manager daily report display. |
| `action_save_data()` | [`main.py#L1346`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1346) | Manually triggers database persistence to JSON. |
| `action_reset_data()` | [`main.py#L1352`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1352) | Prompts for confirmation and resets clinic database. |
| `action_export_report()` | [`main.py#L1373`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1373) | Exports daily clinic report to text file. |
| `action_patient_history()` | [`main.py#L1389`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1389) | Displays completed visit history with cache tracking. |
| `action_view_own_appointments()` | [`main.py#L1427`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1427) | Displays appointments scoped to patient ID with 30-min slot times. |
| `action_view_own_queue_position()` | [`main.py#L1447`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1447) | Displays patient live queue rank, priority, and total waiting count. |
| `action_view_own_history()` | [`main.py#L1482`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1482) | Displays completed visits for patient with memoization cache indicator. |

### 8. Menus, Portals & Main Application Entry
| Function | Direct Code Link | Description |
|---|---|---|
| `run_staff_menu()` | [`main.py#L1511`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1511) | Staff 13-option interactive management loop. |
| `run_doctor_menu()` | [`main.py#L1568`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1568) | Doctor 5-option clinical portal loop. |
| `run_patient_portal()` | [`main.py#L1600`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1600) | Read-only patient portal loop scoped to patient ID. |
| `patient_lookup()` | [`main.py#L1630`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1630) | Passwordless Patient ID input and portal gateway. |
| `login_screen()` | [`main.py#L1649`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1649) | Authentication screen for Staff and Doctor users. |
| `opening_screen()` | [`main.py#L1671`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1671) | Opening screen dispatching to Staff/Doc login, Patient lookup, or Exit. |
| `main()` | [`main.py#L1702`](https://github.com/mohamed-elhosary1/SIC-Smart-Clinic/blob/main/main.py#L1702) | Application entry point with database auto-load and graceful exit autosave. |

