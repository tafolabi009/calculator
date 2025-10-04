"""
Unit tests for Database functionality
"""
import unittest
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'advanced_graphing_calculator', 'graphing_calculator'))

from database import AdvancedDatabase


class TestDatabase(unittest.TestCase):
    """Test cases for AdvancedDatabase"""

    def setUp(self):
        """Set up test database"""
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize database with temp file
        self.db = AdvancedDatabase()
        self.db.db_file = self.temp_db_path
        self.db.init_database()

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    def test_database_initialization(self):
        """Test database initializes correctly"""
        self.assertIsInstance(self.db, AdvancedDatabase)
        self.assertTrue(os.path.exists(self.temp_db_path))

    def test_add_user(self):
        """Test adding a new user"""
        result = self.db.add_user(
            username='testuser',
            password='testpass123',
            role='student',
            full_name='Test User',
            email='test@example.com'
        )
        self.assertTrue(result)

    def test_add_duplicate_user(self):
        """Test adding duplicate user fails"""
        self.db.add_user('testuser', 'pass', 'student', 'Test', 'test@test.com')
        result = self.db.add_user('testuser', 'pass2', 'student', 'Test2', 'test2@test.com')
        self.assertFalse(result)

    def test_verify_user_valid(self):
        """Test verifying valid user credentials"""
        self.db.add_user('testuser', 'testpass', 'student', 'Test', 'test@test.com')
        user_data = self.db.verify_user('testuser', 'testpass')
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['role'], 'student')

    def test_verify_user_invalid(self):
        """Test verifying invalid credentials"""
        self.db.add_user('testuser', 'testpass', 'student', 'Test', 'test@test.com')
        user_data = self.db.verify_user('testuser', 'wrongpass')
        self.assertIsNone(user_data)


if __name__ == '__main__':
    unittest.main()
