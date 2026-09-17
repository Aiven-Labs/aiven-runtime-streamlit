import os
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from starter import connection_options, database_status

PASSWORD = "test-only-password-123456"


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"APP_PASSWORD": PASSWORD, "DATABASE_URL": "", "PG_CA_CERT_BASE64": ""})
        self.env.start()
        self.addCleanup(self.env.stop)

    def login(self):
        app = AppTest.from_file("../app.py").run()
        app.text_input[0].input(PASSWORD)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        return app

    def test_login_blocks_content_and_rejects_wrong_password(self):
        app = AppTest.from_file("../app.py").run()
        self.assertEqual(len(app.metric), 0)
        app.text_input[0].input("wrong")
        app.button[0].click().run()
        self.assertEqual(app.error[0].value, "Incorrect password.")
        self.assertEqual(len(app.metric), 0)

    def test_login_filter_empty_selection_and_logout(self):
        app = self.login()
        self.assertEqual(app.metric[0].value, "42")
        app.multiselect[0].set_value(["Alpha"])
        app.slider[0].set_value(7).run()
        self.assertEqual(app.metric[0].value, "7")
        app.multiselect[0].set_value([]).run()
        self.assertEqual(app.metric[0].value, "0")
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == "Sign out").click().run()
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(app.text_input[0].label, "Password")

    def test_missing_password_fails_closed(self):
        os.environ["APP_PASSWORD"] = ""
        app = AppTest.from_file("../app.py").run()
        self.assertTrue(app.error)
        self.assertEqual(len(app.metric), 0)

    def test_uri_cannot_disable_tls_or_readonly_timeout(self):
        options = connection_options("postgresql://demo:p%40ss@example.com:1234/defaultdb?sslmode=disable&options=-c%20statement_timeout%3D0", "/tmp/ca.pem")
        self.assertEqual(options["password"], "p@ss")
        self.assertEqual(options["sslmode"], "verify-full")
        self.assertIn("default_transaction_read_only=on", options["options"])
        self.assertIn("statement_timeout=5000", options["options"])

    def test_database_errors_do_not_leak_credentials(self):
        os.environ["DATABASE_URL"] = "postgresql://user:secret@example.com/defaultdb"
        app = self.login()
        with patch("starter.database_status", side_effect=RuntimeError("secret")):
            next(b for b in app.button if b.label == "Test connection").click().run()
        self.assertEqual(len(app.error), 1)
        self.assertNotIn("secret", app.error[0].value)
        self.assertFalse(app.exception)

    def test_missing_ca_cannot_connect(self):
        os.environ["DATABASE_URL"] = "postgresql://example.com/defaultdb"
        with patch("starter.psycopg.connect") as connect:
            with self.assertRaises(ValueError):
                database_status()
            connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
