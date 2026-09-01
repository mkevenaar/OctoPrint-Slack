from importlib import metadata


def test_octoprint_entry_point_is_installed():
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        plugins = entry_points.select(group="octoprint.plugin", name="slack")
    else:
        plugins = [
            entry_point
            for entry_point in entry_points.get("octoprint.plugin", ())
            if entry_point.name == "slack"
        ]

    plugins = list(plugins)
    assert len(plugins) == 1
    assert plugins[0].value == "octoprint_slack"


def test_package_version_matches_release():
    assert metadata.version("OctoPrint-Slack") == "0.3.0"
