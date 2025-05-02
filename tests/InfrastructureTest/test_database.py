import unittest
import importlib
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Ensure the db module is reloaded fresh for each test
        # This prevents state from previous tests affecting the current test
        import infrastructure.database.db
        importlib.reload(infrastructure.database.db)

    @patch('sqlalchemy.orm.Session')
    @patch('infrastructure.database.db.SessionLocal')
    def test_get_db(self, mock_session_local, mock_session_class):
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        from infrastructure.database.db import get_db
        db_generator = get_db()
        db = next(db_generator)
        mock_session_local.assert_called_once()
        self.assertEqual(db, mock_session)
        try:
            next(db_generator)
            self.fail("Expected StopIteration")
        except StopIteration:
            pass
        mock_session.close.assert_called_once()

    @patch('sqlalchemy.create_engine')
    def test_engine_creation(self, mock_create_engine):
        from infrastructure.database import db
        importlib.reload(db)
        mock_create_engine.assert_called_once()
        args, kwargs = mock_create_engine.call_args
        self.assertEqual(args[0], "sqlite:///banking_system.database")
        self.assertEqual(kwargs["echo"], True)

    @patch('sqlalchemy.ext.declarative.declarative_base')
    def test_base_creation(self, mock_declarative_base):
        from infrastructure.database import db
        importlib.reload(db)
        mock_declarative_base.assert_called_once()

    @patch('sqlalchemy.orm.sessionmaker')
    def test_session_local_creation(self, mock_sessionmaker):
        from infrastructure.database import db
        importlib.reload(db)
        mock_sessionmaker.assert_called_once()
        kwargs = mock_sessionmaker.call_args[1]
        self.assertEqual(kwargs["autocommit"], False)
        self.assertEqual(kwargs["autoflush"], False)

if __name__ == '__main__':
    unittest.main()