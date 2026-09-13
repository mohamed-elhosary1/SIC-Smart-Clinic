import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pytest

from smart_clinic.core import (
    ClinicManager,
    Doctor,
    RegularPatient,
    EmergencyPatient,
    get_data_path,
    get_report_path,
)

def test_save_and_load_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "test_clinic_data.json"

        # 1. Create and populate manager
        mgr1 = ClinicManager(base_fee=120.0)
        doc = Doctor("doctor-1", "Dr. Magdi", "01012345678", "Cardiology")
        pat = RegularPatient("patient-1", "Mo Salah", "01112345678", 32, "Checkup")
        mgr1.add_doctor(doc)
        mgr1.register_patient(pat)
        slot = datetime(2026, 10, 1, 9, 30)
        mgr1.book_appointment("patient-1", "doctor-1", slot)

        # 2. Save
        saved = mgr1.save_to_file(json_path, silent=True)
        assert saved is True
        assert json_path.exists()

        # 3. Load into fresh manager
        mgr2 = ClinicManager(base_fee=100.0)
        loaded = mgr2.load_from_file(json_path)
        assert loaded is True
        assert len(mgr2.doctors) == 1
        assert len(mgr2.patients) == 1
        assert len(mgr2.appointments) == 1
        assert "doctor-1" in mgr2.doctors
        assert "patient-1" in mgr2.patients
        assert slot in mgr2.booked_date["doctor-1"]

def test_corrupt_file_backup_and_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        corrupt_path = Path(tmpdir) / "corrupt_data.json"
        # Write corrupted syntax
        corrupt_path.write_text("{ corrupt json invalid ...", encoding="utf-8")

        mgr = ClinicManager()
        loaded = mgr.load_from_file(corrupt_path)
        assert loaded is True

        # Ensure backup was created
        bak_path = Path(str(corrupt_path) + ".bak")
        assert bak_path.exists()

def test_daily_report_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "daily_report.txt"
        mgr = ClinicManager(base_fee=100.0)
        doc = Doctor("doctor-1", "Dr. Magdi", "01012345678", "Cardiology")
        pat = EmergencyPatient("patient-1", "Mo Salah", "01112345678", 32, "Chest Pain")
        mgr.add_doctor(doc)
        mgr.register_patient(pat)
        mgr.book_appointment("patient-1", "doctor-1", datetime.now() + timedelta(days=1))

        success = mgr.export_report_to_file(report_path)
        assert success is True
        assert Path(report_path).exists()
        content = Path(report_path).read_text(encoding="utf-8")
        assert "CLINIC DAILY REPORT" in content
        assert "Registered Patients" in content
