from fastapi.testclient import TestClient

from src.hlpr.api.main import app

client = TestClient(app)


class TestJobsContract:
    """Contract tests for GET /jobs/{job_id} endpoint"""

    def test_get_job_status_success(self):
        """Test successful job status retrieval"""
        # This test will fail until the endpoint is implemented
        # Using a valid UUID format
        job_id = "12345678-1234-5678-9012-123456789012"
        response = client.get(f"/jobs/{job_id}")

        # Could be 200 if job exists, or 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "type" in data
            assert data["type"] in ["DOCUMENT_SUMMARY", "EMAIL_PROCESS", "MEETING_ANALYSIS"]
            assert "status" in data
            assert data["status"] in ["QUEUED", "RUNNING", "COMPLETED", "FAILED"]
            assert "progress_percent" in data
            assert 0 <= data["progress_percent"] <= 100
            assert "created_at" in data

    def test_get_job_status_not_found(self):
        """Test job status for non-existent job"""
        job_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "error_code" in data

    def test_get_job_status_invalid_uuid(self):
        """Test job status with invalid UUID format"""
        job_id = "invalid-job-id"
        response = client.get(f"/jobs/{job_id}")

        # Should return 422 for invalid UUID format
        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_get_job_status_completed_job(self):
        """Test status of a completed job"""
        # This would require a job that actually exists and is completed
        # Placeholder for future implementation

    def test_get_job_status_running_job(self):
        """Test status of a running job"""
        # This would require a job that is currently running
        # Placeholder for future implementation

    def test_get_job_status_with_result_data(self):
        """Test job status that includes result data"""
        # For completed jobs, should include result_data
        # Placeholder for future implementation
