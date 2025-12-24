import pytest
from app import app


@pytest.fixture
def client():
    """Create Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_status_code(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Test health endpoint response structure"""
        response = client.get('/health')
        data = response.get_json()
        assert 'status' in data
        assert 'service' in data
        assert 'environment' in data

    def test_health_status_value(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get('/health')
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestMainEndpoint:
    """Tests for / endpoint"""

    def test_main_status_code(self, client):
        """Test main endpoint returns 200"""
        response = client.get('/')
        assert response.status_code == 200

    def test_main_response_structure(self, client):
        """Test main endpoint response structure"""
        response = client.get('/')
        data = response.get_json()
        assert 'message' in data
        assert 'version' in data
        assert 'environment' in data
        assert 'status' in data

    def test_main_message(self, client):
        """Test main endpoint message content"""
        response = client.get('/')
        data = response.get_json()
        assert 'Hello from CI/CD Python App!' in data['message']


class TestInfoEndpoint:
    """Tests for /info endpoint"""

    def test_info_status_code(self, client):
        """Test info endpoint returns 200"""
        response = client.get('/info')
        assert response.status_code == 200

    def test_info_response_structure(self, client):
        """Test info endpoint response structure"""
        response = client.get('/info')
        data = response.get_json()
        assert 'app_name' in data
        assert 'version' in data
        assert 'description' in data
        assert 'endpoints' in data

    def test_info_endpoints(self, client):
        """Test info endpoint lists all endpoints"""
        response = client.get('/info')
        data = response.get_json()
        endpoints = data['endpoints']
        assert '/' in endpoints
        assert '/health' in endpoints
        assert '/info' in endpoints


class TestErrorHandling:
    """Tests for error handling"""

    def test_not_found_endpoint(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method"""
        response = client.post('/')
        assert response.status_code in [405, 404]  # Depends on Flask config


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
