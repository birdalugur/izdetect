
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'api'))
sys.path.append(os.path.join(os.getcwd(), 'services'))

class TestDBRefactor(unittest.TestCase):
    def test_api_db_imports(self):
        """Test that api/db.py can be imported and uses db_client"""
        with patch('api.db_client.db_client') as mock_client:
            import api.db
            self.assertTrue(hasattr(api.db, 'get_active_notifications'))

    def test_services_db_imports(self):
        """Test that services/core/db.py can be imported"""
        with patch('services.core.db_client.db_client') as mock_client:
            import services.core.db
            self.assertTrue(hasattr(services.core.db, 'add_notification'))

    def test_db_service_structure(self):
        """Test that db_service files exist"""
        self.assertTrue(os.path.exists('db_service/main.py'))
        self.assertTrue(os.path.exists('db_service/core/repository.py'))
        self.assertTrue(os.path.exists('db_service/routes/api.py'))

if __name__ == '__main__':
    unittest.main()
