from importlib import metadata


def test_octoprint_entry_point_is_installed():
    distribution = metadata.distribution("OctoPrint-Slack")
    plugins = [
        entry_point
        for entry_point in distribution.entry_points
        if entry_point.group == "octoprint.plugin"
        and entry_point.name == "slack"
    ]

    assert len(plugins) == 1
    assert plugins[0].value == "octoprint_slack"


def test_package_version_matches_release():
    assert metadata.version("OctoPrint-Slack") == "0.3.0"
