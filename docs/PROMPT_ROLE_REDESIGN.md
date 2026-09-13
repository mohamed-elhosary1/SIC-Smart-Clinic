# Architecture Specification: Role-Based Access & Simplified Patient Lookup

**Project:** Smart Clinic Queue System  
**Program:** Chapter 3 Capstone — Samsung Innovation Campus  
**Target Codebase:** `main.py` (Single-File Architecture)

---

## 1. Overview & Problem Statement

In the initial RBAC design, patients were treated as authenticated system users (`PatientUser`) requiring a password. During registration, patients had to define credentials, and the login screen combined authentication with patient self-registration.

In real-world clinics and hospital reception workflows:
- Patients do **not** register software user accounts with passwords at a front desk kiosk.
- Front-desk staff issue a patient record card containing an ID (e.g. `patient-123`).
- Patients check in or track their queue and appointments using their assigned **Patient ID**.
- Full authentication with credentials should remain strictly reserved for medical and administrative staff (`StaffUser` and `DoctorUser`).

---

## 2. Architecture & Design Principles

### 2.1 Separation of Concerns
1. **Administrative & Medical Staff (Authenticated Users):**
   - Base Class: `User(username, password, allowed_actions)`
   - Subclasses:
     - `StaffUser`: Unrestricted administrative privileges across all operations.
     - `DoctorUser`: Restricted clinical actions (`view_queue`, `update_visit_status`, `daily_report`, `view_history`).
   - Authentication: Looked up exclusively against `USERS_DB`.
2. **Patients (Domain Entities, ID-Lookup Only):**
   - Base Class: `Person(person_id, name, phone)`
   - Subclasses: `Patient` -> `RegularPatient`, `EmergencyPatient`.
   - **No password attribute**: Removed completely from models, JSON schema, and registration UI.
   - Access Mechanism: Direct ID lookup (`patient_lookup(manager)`).

---

## 3. Screen Hierarchy & User Experience

```mermaid
flowchart TD
    Start([Application Start: main()]) --> Opening[opening_screen]
    
    Opening -->|Choice 1| Login[login_screen]
    Opening -->|Choice 2| Lookup[patient_lookup]
    Opening -->|Choice 3| Exit[Graceful Exit & Auto-Save]

    Login -->|Invalid| Login
    Login -->|StaffUser| StaffMenu[run_staff_menu]
    Login -->|DoctorUser| DoctorMenu[run_doctor_menu]

    StaffMenu -->|Option 13: Logout| Opening
    DoctorMenu -->|Option 5: Logout| Opening

    Lookup -->|Enter Patient ID| ValidateID{ID Exists?}
    ValidateID -->|No| LookupError[Show Error & Retry / Cancel]
    LookupError --> Lookup
    ValidateID -->|Yes| PatientPortal[run_patient_portal]
    PatientPortal -->|Option 4: Back| Opening
```

### 3.1 Opening Screen (`opening_screen`)
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

### 3.2 Staff / Doctor Login Screen (`login_screen`)
- Prompts for `Username` and `Password`.
- Authenticates against `USERS_DB`:
  - `staff` / `staff123` -> `StaffUser`
  - `doctor` / `doc123` -> `DoctorUser`
- Default accounts are **hidden** from the UI header to maintain production UI cleanliness.

### 3.3 Patient Lookup & Portal (`patient_lookup` & `run_patient_portal`)
- Prompts for `Patient ID` (e.g. `patient-123`).
- Validates that the ID exists in `ClinicManager.patients`.
- Launches `run_patient_portal(manager, patient_id)`:
  - `[1] My Appointments`
  - `[2] My Queue Position`
  - `[3] My Visit History`
  - `[4] Back to Main Screen`
- Entirely read-only; scoped strictly to the given `patient_id`.

---

## 4. Key Security & Method Contracts

1. **`USERS_DB` Definition**:
   ```python
   USERS_DB = {
       "staff": {"password": "staff123", "factory": lambda u, p: StaffUser(u, p)},
       "doctor": {"password": "doc123", "factory": lambda u, p: DoctorUser(u, p)},
   }
   ```
2. **`authenticate(username, password)`**:
   Validates credentials against `USERS_DB` only. Raises `ClinicError` on invalid credentials.
3. **`ClinicManager.get_patient_completed_visits`**:
   - Permission check `self.current_user.has_permission("view_history")` only runs if `self.current_user is not None`.
   - When called during patient lookup (`self.current_user == None`), viewing own history is granted seamlessly.
4. **Data Persistence (`clinic_data.json`)**:
   - Patient serialized dictionaries omit any password fields.
