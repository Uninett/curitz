import datetime
from pathlib import Path
import sys
import unittest
from ipaddress import ip_address

from curitz.cli import Config, build_config, parse_args


class ParseArgsTest(unittest.TestCase):

    def test_utf8_is_false_if_unset_or_ascii_set(self):
        args = parse_args([])
        self.assertFalse(args.utf8)
        args = parse_args(['--ascii'])
        self.assertFalse(args.utf8)

    def test_utf8_is_true_if_explicitly_set(self):
        args = parse_args(['--utf8'])
        self.assertTrue(args.utf8)

    def test_all_args_have_defaults(self):
        args = parse_args([])
        default_args = {
            'arrow': False,
            'autoremove': False,
            'config': '~/.ritz.tcl',
            'debug': False,
            'kiosk': False,
            'nocolor': False,
            'profile': 'default',
            'profiles': False,
            'utf8': False,
        }
        self.assertEqual(vars(args), default_args)


class BuildConfigTest(unittest.TestCase):
    BOOLEAN_FLAGS = ('UTF8', 'kiosk', 'autoremove', 'nocolor')

    def test_profile_arg_set_copies_dict_contents(self):
        conf = {'default': {'foo': 5}}
        config = build_config(conf, Config())
        self.assertTrue(hasattr(config, 'foo'))
        self.assertEqual(config.foo, 5)

    def test_all_bool_args_unset(self):
        args = Config({})
        config = build_config({}, args)
        self.assertEqual(config.arrow, '')
        for flag in self.BOOLEAN_FLAGS:
            value = getattr(config, flag, 'DUMMY')
            self.assertNotEqual(value, 'DUMMY', flag)  # All should be set
            self.assertFalse(value)

    def test_all_bool_args_false(self):
        args = Config({
            'utf8': False,
            'kiosk': False,
            'autoremove': False,
            'nocolor': False,
            'arrow': False,
        })
        config = build_config({}, args)
        self.assertEqual(config.arrow, '')
        for flag in self.BOOLEAN_FLAGS:
            value = getattr(config, flag, 'DUMMY')
            self.assertNotEqual(value, 'DUMMY', flag)  # All should be set
            self.assertFalse(value)

    def test_all_bool_args_true(self):
        args = Config({
            'utf8': True,
            'kiosk': True,
            'autoremove': True,
            'nocolor': True,
            'arrow': True,
        })
        config = build_config({}, args)
        self.assertEqual(config.arrow, '>')
        for flag in self.BOOLEAN_FLAGS:
            value = getattr(config, flag, 'DUMMY')
            self.assertNotEqual(value, 'DUMMY', flag)  # All should be set
            self.assertTrue(value)
