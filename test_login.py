import unittest
from unittest.mock import patch, MagicMock
import login


class LoginTests(unittest.TestCase):
    def test_browser_can_open_http_campus_portal(self):
        self.assertTrue(hasattr(login, 'create_driver'), 'browser factory needed for regression')
        with patch.object(login.webdriver, 'Chrome') as chrome:
            login.create_driver()
        options = chrome.call_args.kwargs['options']
        self.assertIn('--disable-features=HttpsFirstBalancedModeAutoEnable', options.arguments)
        self.assertFalse(options.accept_insecure_certs)

    def test_campus_status_handles_offline_online_and_invalid_responses(self):
        self.assertTrue(hasattr(login, 'portal_state'), 'explicit portal state required')
        online = 'account,1,2,3,4,5,6,7,10.81.39.147,0'
        for response, expected in [('not_online_error', 'offline'), (online, 'online'),
                                   ('<html>error</html>', 'unknown'), ('', 'unknown')]:
            with self.subTest(response=response), patch.object(login, 'fetch_text', return_value=response):
                self.assertEqual(login.portal_state('http://124.17.100.50/'), expected)
        with patch.object(login, 'fetch_text', side_effect=OSError('timeout')):
            self.assertEqual(login.portal_state('http://124.17.100.50/'), 'unknown')

    def test_external_check_falls_back_to_an_independent_https_site(self):
        self.assertTrue(hasattr(login, 'fetch_text'), 'bounded HTTP probe required')
        with patch.object(login, 'fetch_text', side_effect=[OSError('DNS failure'), 'valid page']) as fetch:
            self.assertTrue(login.check_network_connection())
        self.assertEqual(fetch.call_count, 2)
        self.assertTrue(all(c.args[0].startswith('https://') for c in fetch.call_args_list))
        with patch.object(login, 'fetch_text', side_effect=OSError('timeout')):
            self.assertFalse(login.check_network_connection())

    def test_online_with_external_failure_does_not_relogin(self):
        self.assertTrue(hasattr(login, 'ensure_connection'), 'verified login cycle required')
        with patch.object(login, 'portal_state', return_value='online'), \
                patch.object(login, 'check_network_connection', return_value=False), \
                patch.object(login, 'create_driver') as create, \
                patch('builtins.print') as output:
            self.assertFalse(login.ensure_connection('http://portal/', 'user', 'secret'))
        create.assert_not_called()
        self.assertNotIn('Login successful', str(output.call_args_list))

    def test_click_without_online_confirmation_never_reports_success(self):
        self.assertTrue(hasattr(login, 'ensure_connection'), 'verified login cycle required')
        driver = MagicMock()
        wait = MagicMock()
        from selenium.common.exceptions import TimeoutException
        wait.until.side_effect = [MagicMock(), MagicMock(), MagicMock(), TimeoutException()]
        with patch.object(login, 'portal_state', return_value='offline'), \
                patch.object(login, 'create_driver', return_value=driver), \
                patch.object(login, 'WebDriverWait', return_value=wait), \
                patch('builtins.print') as output:
            self.assertFalse(login.ensure_connection('http://portal/', 'user', 'secret'))
        driver.quit.assert_called_once()
        self.assertNotIn('Login successful', str(output.call_args_list))

    def test_verified_login_reports_success_and_closes_browser(self):
        self.assertTrue(hasattr(login, 'ensure_connection'), 'verified login cycle required')
        with patch.object(login, 'portal_state', side_effect=['offline', 'online']), \
                patch.object(login, 'check_network_connection', return_value=True), \
                patch.object(login, 'create_driver') as create, \
                patch.object(login, 'WebDriverWait'), patch('builtins.print') as output:
            self.assertTrue(login.ensure_connection('http://portal/', 'user', 'secret'))
        create.return_value.quit.assert_called_once()
        self.assertIn('Login successful', str(output.call_args_list))

    def test_unknown_portal_state_does_not_submit_credentials(self):
        self.assertTrue(hasattr(login, 'ensure_connection'), 'verified login cycle required')
        with patch.object(login, 'portal_state', return_value='unknown'), \
                patch.object(login, 'create_driver') as create:
            self.assertFalse(login.ensure_connection('http://portal/', 'user', 'secret'))
        create.assert_not_called()

    def test_keepalive_retries_failure_without_busy_loop(self):
        with patch.object(login, 'ensure_connection', side_effect=[False, True, False, False]), \
                patch.object(login.time, 'sleep') as sleep:
            self.assertFalse(login.run('http://portal/', 'user', 'secret', True, 2))
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [60, 60, 60, 120])

    def test_once_mode_returns_failure_without_retry(self):
        with patch.object(login, 'ensure_connection', return_value=False) as ensure, \
                patch.object(login.time, 'sleep') as sleep:
            self.assertFalse(login.run('http://portal/', 'user', 'secret', False, -1))
        ensure.assert_called_once()
        sleep.assert_not_called()

    def test_cli_parses_false_and_preserves_existing_true_syntax(self):
        self.assertTrue(hasattr(login, 'parse_bool'), 'bool("False") must not enable keepalive')
        self.assertFalse(login.parse_bool('False'))
        self.assertTrue(login.parse_bool('True'))
        with self.assertRaises(Exception):
            login.parse_bool('invalid')


if __name__ == '__main__':
    unittest.main()
