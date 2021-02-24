"""
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
"""

import os

import pytest
import salt.states.ssh_known_hosts as ssh_known_hosts
from tests.support.mock import MagicMock, patch


@pytest.fixture
def configure_loader_modules():
    return {ssh_known_hosts: {}}


def test_present():
    """
    Test to verify that the specified host is known by the specified user.
    """
    name = "github.com"
    user = "root"
    key = "16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48"
    fingerprint = [key]

    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    with patch.dict(ssh_known_hosts.__opts__, {"test": True}):
        with patch.object(os.path, "isabs", MagicMock(return_value=False)):
            comt = 'If not specifying a "user", ' 'specify an absolute "config".'
            ret.update({"comment": comt})
            assert ssh_known_hosts.present(name) == ret

        comt = 'Specify either "key" or "fingerprint", not both.'
        ret.update({"comment": comt})
        assert ssh_known_hosts.present(name, user, key=key, fingerprint=[key]) == ret

        comt = 'Required argument "enc" if using "key" argument.'
        ret.update({"comment": comt})
        assert ssh_known_hosts.present(name, user, key=key) == ret

        mock = MagicMock(side_effect=["exists", "add", "update"])
        with patch.dict(ssh_known_hosts.__salt__, {"ssh.check_known_host": mock}):
            comt = "Host github.com is already in .ssh/known_hosts"
            ret.update({"comment": comt, "result": True})
            assert ssh_known_hosts.present(name, user) == ret

            comt = "Key for github.com is set to be" " added to .ssh/known_hosts"
            ret.update({"comment": comt, "result": None})
            assert ssh_known_hosts.present(name, user) == ret

            comt = "Key for github.com is set to be " "updated in .ssh/known_hosts"
            ret.update({"comment": comt})
            assert ssh_known_hosts.present(name, user) == ret

    with patch.dict(ssh_known_hosts.__opts__, {"test": False}):
        result = {"status": "exists", "error": ""}
        mock = MagicMock(return_value=result)
        with patch.dict(ssh_known_hosts.__salt__, {"ssh.set_known_host": mock}):
            comt = "github.com already exists in .ssh/known_hosts"
            ret.update({"comment": comt, "result": True})
            assert ssh_known_hosts.present(name, user) == ret

        result = {"status": "error", "error": ""}
        mock = MagicMock(return_value=result)
        with patch.dict(ssh_known_hosts.__salt__, {"ssh.set_known_host": mock}):
            ret.update({"comment": "", "result": False})
            assert ssh_known_hosts.present(name, user) == ret

        result = {
            "status": "updated",
            "error": "",
            "new": [{"fingerprint": fingerprint, "key": key}],
            "old": "",
        }
        mock = MagicMock(return_value=result)
        with patch.dict(ssh_known_hosts.__salt__, {"ssh.set_known_host": mock}):
            comt = "{}'s key saved to .ssh/known_hosts (key: {})".format(name, key)
            ret.update(
                {
                    "comment": comt,
                    "result": True,
                    "changes": {
                        "new": [{"fingerprint": fingerprint, "key": key}],
                        "old": "",
                    },
                }
            )
            assert ssh_known_hosts.present(name, user, key=key) == ret

            comt = "{}'s key saved to .ssh/known_hosts (fingerprint: {})".format(
                name, fingerprint
            )
            ret.update({"comment": comt})
            assert ssh_known_hosts.present(name, user) == ret


def test_absent():
    """
    Test to verifies that the specified host is not known by the given user.
    """
    name = "github.com"
    user = "root"

    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    with patch.object(os.path, "isabs", MagicMock(return_value=False)):
        comt = 'If not specifying a "user", ' 'specify an absolute "config".'
        ret.update({"comment": comt})
        assert ssh_known_hosts.absent(name) == ret

    mock = MagicMock(return_value=False)
    with patch.dict(ssh_known_hosts.__salt__, {"ssh.get_known_host_entries": mock}):
        comt = "Host is already absent"
        ret.update({"comment": comt, "result": True})
        assert ssh_known_hosts.absent(name, user) == ret

    mock = MagicMock(return_value=True)
    with patch.dict(ssh_known_hosts.__salt__, {"ssh.get_known_host_entries": mock}):
        with patch.dict(ssh_known_hosts.__opts__, {"test": True}):
            comt = "Key for github.com is set to be" " removed from .ssh/known_hosts"
            ret.update({"comment": comt, "result": None})
            assert ssh_known_hosts.absent(name, user) == ret

        with patch.dict(ssh_known_hosts.__opts__, {"test": False}):
            result = {"status": "error", "error": ""}
            mock = MagicMock(return_value=result)
            with patch.dict(ssh_known_hosts.__salt__, {"ssh.rm_known_host": mock}):
                ret.update({"comment": "", "result": False})
                assert ssh_known_hosts.absent(name, user) == ret

            result = {"status": "removed", "error": "", "comment": "removed"}
            mock = MagicMock(return_value=result)
            with patch.dict(ssh_known_hosts.__salt__, {"ssh.rm_known_host": mock}):
                ret.update(
                    {
                        "comment": "removed",
                        "result": True,
                        "changes": {"new": None, "old": True},
                    }
                )
                assert ssh_known_hosts.absent(name, user) == ret
