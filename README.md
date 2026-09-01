# OctoPrint Slack Integration

[![Version](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=version&url=https://api.github.com/repos/mkevenaar/OctoPrint-Slack/releases&query=$[0].name)]()
[![Released](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=released&url=https://api.github.com/repos/mkevenaar/OctoPrint-Slack/releases&query=$[0].published_at)]()
![GitHub Releases (by Release)](https://img.shields.io/github/downloads/mkevenaar/OctoPrint-Slack/latest/total.svg)

Send messages to your group's Slack chat when printing events happen!
You need to set up an [Incoming Webhook](https://my.slack.com/services/new/incoming-webhook) integration on the Slack side to use this.

## Compatibility

OctoPrint-Slack 0.3.0 and newer supports OctoPrint 1.8.3 and newer, including OctoPrint 2.x, on Python 3.7 through 3.x. OctoPrint 2.0 itself requires Python 3.9 or newer.

## Features

* Select which events you want to trigger a chat notification for
* Customizable messages for each event
* Customize bot icon and username in Slack chat
* Sends elapsed time of print after finished

## Screenshots

![Slack chat with messages from plugin.](/screenshots/slack.png?raw=true)
![Plugin settings screenshot.](/screenshots/settings.png?raw=true)
![Plugin settings screenshot.](/screenshots/settings2.png?raw=true)

## Installation

Follow the instructions provided by [OctoPrint](https://plugins.octoprint.org/help/installation/).

## Privacy

The plugin sends configured print-event information to the Slack Incoming Webhook supplied by the OctoPrint administrator. See the [privacy policy](PRIVACY.md) for the exact data involved.
