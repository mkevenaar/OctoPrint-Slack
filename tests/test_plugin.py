from copy import deepcopy
from unittest.mock import Mock

import pytest
import requests
from octoprint.filemanager.destinations import FileDestinations

import octoprint_slack
from octoprint_slack import SlackPlugin


PRINT_EVENTS = (
    "PrintStarted",
    "PrintFailed",
    "PrintCancelled",
    "PrintDone",
    "PrintPaused",
    "PrintResumed",
)


class FakeSettings:
    def __init__(self, data):
        self.data = deepcopy(data)

    def get(self, path, merged=False):
        value = self.data
        for item in path:
            if not isinstance(value, dict) or item not in value:
                return None
            value = value[item]
        return deepcopy(value) if merged else value

    def set(self, path, value):
        target = self.data
        for item in path[:-1]:
            target = target.setdefault(item, {})
        target[path[-1]] = value

    def set_boolean(self, path, value):
        self.set(path, bool(value))

    def remove(self, path):
        target = self.data
        for item in path[:-1]:
            target = target[item]
        target.pop(path[-1], None)


@pytest.fixture
def plugin():
    implementation = SlackPlugin()
    settings = implementation.get_settings_defaults()
    settings.update(
        webhook_url="https://hooks.slack.test/services/example",
        bot_username="OctoPrint",
        bot_icon_url="",
        bot_icon_emoji=":printer:",
        bot_channel="printing",
    )
    implementation._settings = FakeSettings(settings)
    implementation._logger = Mock()
    return implementation


@pytest.fixture
def successful_post(monkeypatch):
    post = Mock(return_value=Mock(ok=True, text="ok"))
    monkeypatch.setattr(octoprint_slack.requests, "post", post)
    return post


@pytest.mark.parametrize("event", PRINT_EVENTS)
def test_supported_print_events_send_a_slack_message(
    plugin, successful_post, event
):
    plugin.on_event(
        event,
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL, "time": 65},
    )

    successful_post.assert_called_once()
    _, kwargs = successful_post.call_args
    assert kwargs["timeout"] == octoprint_slack.SLACK_REQUEST_TIMEOUT
    assert "data" not in kwargs
    assert kwargs["json"]["username"] == "OctoPrint"
    assert kwargs["json"]["icon_emoji"] == ":printer:"
    assert kwargs["json"]["channel"] == "#printing"


@pytest.mark.parametrize(
    ("origin", "expected"),
    (
        (FileDestinations.LOCAL, "Local"),
        (FileDestinations.SDCARD, "Printer"),
        (getattr(FileDestinations, "PRINTER", FileDestinations.SDCARD), "Printer"),
        ("external_storage", "external_storage"),
    ),
)
def test_storage_origin_is_displayed_compatibly(
    plugin, successful_post, origin, expected
):
    plugin.on_event("PrintStarted", {"name": "cube.gcode", "origin": origin})

    message = successful_post.call_args.kwargs["json"]
    fields = message["attachments"][0]["fields"]
    assert {"title": "Origin", "value": expected, "short": True} in fields


def test_elapsed_time_is_added_for_completed_print(plugin, successful_post):
    plugin.on_event(
        "PrintDone",
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL, "time": 65},
    )

    attachment = successful_post.call_args.kwargs["json"]["attachments"][0]
    assert any(field["title"] == "Time" for field in attachment["fields"])
    assert "{time}" not in attachment["fallback"]


def test_disabled_event_does_not_send(plugin, successful_post):
    plugin._settings.data["print_events"]["PrintStarted"]["Enabled"] = False

    plugin.on_event(
        "PrintStarted",
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL},
    )

    successful_post.assert_not_called()


def test_unknown_event_does_not_send(plugin, successful_post):
    plugin.on_event("Connected", {})

    successful_post.assert_not_called()


def test_missing_webhook_does_not_send(plugin, successful_post):
    plugin._settings.data["webhook_url"] = ""

    plugin.on_event(
        "PrintStarted",
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL},
    )

    successful_post.assert_not_called()
    plugin._logger.warning.assert_called_once()


def test_network_errors_do_not_escape_event_handler(plugin, monkeypatch):
    post = Mock(side_effect=requests.Timeout("timed out"))
    monkeypatch.setattr(octoprint_slack.requests, "post", post)

    plugin.on_event(
        "PrintStarted",
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL},
    )

    plugin._logger.exception.assert_called_once()


def test_unsuccessful_response_is_logged(plugin, monkeypatch):
    post = Mock(return_value=Mock(ok=False, text="invalid_payload"))
    monkeypatch.setattr(octoprint_slack.requests, "post", post)

    plugin.on_event(
        "PrintStarted",
        {"name": "cube.gcode", "origin": FileDestinations.LOCAL},
    )

    plugin._logger.error.assert_called_once()


def test_sensitive_setting_hooks_and_autoescaping(plugin):
    assert plugin.get_settings_restricted_paths() == {
        "admin": [["webhook_url"]]
    }
    assert plugin.get_settings_reauth_requirements() == {"webhook_url": True}
    assert plugin.is_template_autoescaped() is True


def test_legacy_settings_are_migrated_without_private_apis():
    plugin = SlackPlugin()
    settings = plugin.get_settings_defaults()
    settings.update(
        enabled=True,
        events={"PrintStarted": False, "PrintDone": True},
    )
    plugin._settings = FakeSettings(settings)

    plugin.on_settings_migrate(target=3, current=2)

    assert plugin._settings.data["print_events"]["PrintStarted"]["Enabled"] is False
    assert plugin._settings.data["enabled"] is None
    assert plugin._settings.data["events"] is None
    assert all(
        "Fallback" not in event_settings
        for event_settings in plugin._settings.data["print_events"].values()
    )
