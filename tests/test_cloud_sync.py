import json
import tempfile
from pathlib import Path
import pytest

from smart_clinic.core.cloud_sync import CloudSyncClient
from smart_clinic.core import ClinicManager, Doctor, RegularPatient

def test_cloud_sync_client_initialization():
    client = CloudSyncClient(enabled=True)
    assert client.enabled is True
    assert client.provider_name in ("Local Resilient Store", "Disabled")
    status = client.get_status()
    assert "status" in status
    assert "provider" in status

def test_cloud_sync_push_and_fetch_mock():
    client = CloudSyncClient(enabled=True)
    sample_data = {
        "patients": [{"person_id": "patient-1", "name": "Test Patient", "phone": "01000000000", "age": 30, "case_type": "Checkup"}],
        "doctors": [{"person_id": "doctor-1", "name": "Dr. Test", "phone": "01011111111", "specialty": "General", "availability": True}],
        "appointments": []
    }
    push_ok = client.push_cloud_data(sample_data)
    assert push_ok is True
    assert client.last_status == "synced"

    fetched = client.fetch_cloud_data()
    assert fetched is not None
    assert fetched["patients"][0]["name"] == "Test Patient"
    assert fetched["doctors"][0]["person_id"] == "doctor-1"

def test_cloud_recovery_when_local_file_missing():
    client = CloudSyncClient(enabled=True)
    sample_data = {
        "patients": [{"person_id": "patient-1", "name": "Recovered Patient", "phone": "01000000000", "age": 28, "case_type": "Flu"}],
        "doctors": [],
        "appointments": []
    }
    client.push_cloud_data(sample_data)

    with tempfile.TemporaryDirectory() as tmpdir:
        missing_file = Path(tmpdir) / "subfolder" / "clinic_data.json"
        assert not missing_file.exists()

        recovered, msg = client.recover_if_needed(missing_file)
        assert recovered is True
        assert missing_file.exists()
        loaded = json.loads(missing_file.read_text(encoding="utf-8"))
        assert loaded["patients"][0]["name"] == "Recovered Patient"

def test_offline_fallback_resilience():
    # Client pointing to an invalid unreachable host
    client = CloudSyncClient(
        enabled=True,
        sync_url="http://127.0.0.1:59999/invalid/endpoint",
        timeout=1
    )
    # Attempting push to unreachable URL should not crash
    client.push_cloud_data({"patients": []})
    status = client.get_status()
    assert status["status"] in ("offline", "synced")

def test_clinic_manager_cloud_integration():
    client = CloudSyncClient(enabled=True)
    mgr = ClinicManager(base_fee=100.0, cloud_sync=client)
    doc = Doctor("doctor-1", "Dr. Magdi", "01012345678", "Cardiology")
    pat = RegularPatient("patient-1", "Mo Salah", "01112345678", 32, "Checkup")
    mgr.add_doctor(doc)
    mgr.register_patient(pat)

    res = mgr.sync_cloud()
    assert res["success"] is True
    assert res["status"] == "synced"

    # Verify cloud client received the data
    cloud_data = client.fetch_cloud_data()
    assert cloud_data is not None
    assert len(cloud_data["patients"]) == 1
    assert len(cloud_data["doctors"]) == 1
