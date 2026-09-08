"""Tests for locating and parsing .ritz.tcl configuration files.

These guard the behaviour that zinolib's own ``parse_tcl_config()`` stopped
providing in 1.0: honouring the exact path curitz is given, including any
directory component, rather than searching a fixed set of directories.
"""

import pytest

from curitz.cli import Config, build_config, read_config


class TestReadConfig:
    def test_when_file_has_a_default_profile_it_should_parse_it_under_the_default_key(
        self, config_file
    ):
        conf = read_config(str(config_file))
        assert conf["default"] == {
            "Secret": "TOKEN_DEFAULT",
            "User": "user_default",
            "Server": "default.example.org",
            "Port": "8001",
        }

    def test_when_file_has_a_named_profile_it_should_parse_it_under_that_name(
        self, config_file
    ):
        conf = read_config(str(config_file))
        assert conf["ALTERNATE"] == {
            "Secret": "TOKEN_ALT",
            "User": "user_alt",
            "Server": "alt.example.org",
            "Port": "8002",
        }

    def test_when_given_a_path_with_directories_it_should_read_that_exact_file(
        self, tmp_path, monkeypatch
    ):
        # A decoy in the location zinolib's own config search would find first:
        # reading the explicit path has to win over it.
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / ".somewhere-else.tcl").write_text("set Server decoy.example.org\n")

        directory = tmp_path / "etc" / "zino"
        directory.mkdir(parents=True)
        config_file = directory / "somewhere-else.tcl"
        config_file.write_text("set Server buried.example.org\n")

        conf = read_config(str(config_file))

        assert conf["default"]["Server"] == "buried.example.org"

    def test_when_given_a_tilde_path_it_should_expand_it(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / ".ritz.tcl").write_text("set Server home.example.org\n")

        conf = read_config("~/.ritz.tcl")

        assert conf["default"]["Server"] == "home.example.org"

    def test_when_a_profile_is_selected_it_should_reach_build_config_as_attributes(
        self, config_file
    ):
        # The migration's real risk is that zinolib 1.x's parse() returns a
        # different dict shape than 0.x did. build_config is what consumes it.
        conf = read_config(str(config_file))

        config = build_config(conf, Config({"profile": "ALTERNATE"}))

        assert config.Server == "alt.example.org"
        assert config.User == "user_alt"
        assert config.Secret == "TOKEN_ALT"
        assert config.Port == "8002"

    def test_when_file_does_not_exist_it_should_raise_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_config(str(tmp_path / "no-such-file.tcl"))


@pytest.fixture
def config_file(tmp_path):
    """A .ritz.tcl with a default profile and one named profile."""
    path = tmp_path / "ritz.tcl"
    path.write_text(
        "set Secret TOKEN_DEFAULT\n"
        "set User user_default\n"
        "set Server default.example.org\n"
        "set Port 8001\n"
        "\n"
        "set _Secret(ALTERNATE) TOKEN_ALT\n"
        "set _User(ALTERNATE) user_alt\n"
        "set _Server(ALTERNATE) alt.example.org\n"
        "set _Port(ALTERNATE) 8002\n"
    )
    return path
