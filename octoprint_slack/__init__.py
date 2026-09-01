import datetime

import octoprint.plugin
import requests
from octoprint.filemanager.destinations import FileDestinations
from octoprint.util import get_formatted_timedelta


SLACK_REQUEST_TIMEOUT = 10


def _display_origin(origin):
    printer_origin = getattr(
        FileDestinations, "PRINTER", FileDestinations.SDCARD
    )
    if origin == FileDestinations.LOCAL:
        return "Local"
    if origin in (FileDestinations.SDCARD, printer_origin):
        return "Printer"
    return origin


class SlackPlugin(
        octoprint.plugin.SettingsPlugin,
        octoprint.plugin.TemplatePlugin,
        octoprint.plugin.EventHandlerPlugin
):
    ##~~ SettingsPlugin
    def get_settings_defaults(self):
        return dict(
            webhook_url="",
            print_events=dict(
                PrintStarted=dict(
                        Enabled=True,
                        Message="A new print has started! :muscle:",
                        Fallback="Print started! Filename: {filename}",
                        Color="good",
                ),
                PrintFailed=dict(
                    Enabled=True,
                    Message="Oh no! The print has failed... :rage2:",
                    Fallback="Print failed! Filename: {filename}",
                    Color="danger",
                ),
                PrintCancelled=dict(
                    Enabled=True,
                    Message="Uh oh... someone cancelled the print! :crying_cat_face:",
                    Fallback="Print cancelled! Filename: {filename}",
                    Color="danger",
                ),
                PrintDone=dict(
                    Enabled=True,
                    Message="Print finished successfully! :thumbsup:",
                    Fallback="Print finished! Filename: {filename}, Time: {time}",
                    Color="good",
                ),
                PrintPaused=dict(
                    Enabled=True,
                    Message="Printing has been paused... :sleeping:",
                    Fallback="Print paused... Filename: {filename}",
                    Color="warning",
                ),
                PrintResumed=dict(
                    Enabled=True,
                    Message="Phew! Printing has been resumed! Back to work... :hammer:",
                    Fallback="Print resumed! Filename: {filename}",
                    Color="good",
                ),
            ),
        )

    def get_settings_restricted_paths(self):
        return dict(admin=[["webhook_url"], ])

    def get_settings_reauth_requirements(self):
        return {"webhook_url": True}

    def get_settings_version(self):
        return 3

    def on_settings_migrate(self, target, current):
        if current in (1, 2):
            events = self._settings.get(['events'])
            # migrate events
            print_events = self._settings.get(['print_events'])
            if events:
                for event in events:
                    if not events[event]:
                        self._settings.set_boolean(
                            ['print_events', event, 'Enabled'], False)
            # remove old settings if there
            self._settings.set(['enabled'], None)
            self._settings.set(['events'], None)
            # clean up old fallback messages from <1.2.7 oversaving
            for event in print_events:
                self._settings.remove(['print_events', event, 'Fallback'])

    ##~~ TemplatePlugin
    def get_template_configs(self):
        return [dict(type="settings", name="Slack", custom_bindings=False)]

    def is_template_autoescaped(self):
        return True

    ##~~ EventPlugin
    def on_event(self, event, payload):
        events = self._settings.get(['print_events'], merged=True)

        if event in events and events[event] and events[event]['Enabled']:

            webhook_url = self._settings.get(['webhook_url'])
            if not webhook_url:
                self._logger.warning("Slack Webhook URL not set!")
                return

            filename = payload["name"]
            origin = _display_origin(payload['origin'])

            message = {}

            # bot display settings

            # if no username is set, it will default to the webhook username
            username = self._settings.get(['bot_username'])
            if username:
                message['username'] = username

            # if an icon is set, use that. if not, use the emoji.
            # if neither are set, it will default to the webhook icon/emoji
            icon_url = self._settings.get(['bot_icon_url'])
            icon_emoji = self._settings.get(['bot_icon_emoji'])
            if icon_url:
                message['icon_url'] = icon_url
            elif icon_emoji:
                message['icon_emoji'] = icon_emoji

            # if a channel is set, use that. if not, just don't send any
            bot_channel = self._settings.get(['bot_channel'])
            if bot_channel:
                if bot_channel[0] != '#':
                    bot_channel = '#' + bot_channel
                message['channel'] = bot_channel

            # message settings
            message['attachments'] = [{}]
            attachment = message['attachments'][0]
            attachment['fields'] = []
            attachment['fields'].append(
                {"title": "Filename", "value": filename, "short": True})
            attachment['fields'].append(
                {"title": "Origin", "value": origin, "short": True})

            # event settings
            event_settings = self._settings.get(
                ['print_events', event], merged=True
            )

            if "time" in payload and payload["time"]:
                elapsed_time = get_formatted_timedelta(
                    datetime.timedelta(seconds=payload["time"]))
            else:
                elapsed_time = ""

            attachment['fallback'] = event_settings['Fallback'].format(
                **{'filename': filename, 'time': elapsed_time})
            attachment['pretext'] = event_settings['Message']
            attachment['color'] = event_settings['Color']
            if elapsed_time != "":
                attachment['fields'].append(
                    {"title": "Time", "value": elapsed_time, "short": True})

            self._logger.debug(
                "Attempting post of Slack message: {}".format(message))
            try:
                res = requests.post(
                    webhook_url,
                    json=message,
                    timeout=SLACK_REQUEST_TIMEOUT,
                )
            except requests.RequestException as e:
                self._logger.exception(
                    "An error occurred connecting to Slack:\n {}".format(e))
                return

            if not res.ok:
                self._logger.error(
                    "An error occurred posting to Slack:\n {}".format(res.text))
                return

            self._logger.debug("Posted event successfully to Slack!")

        else:
            self._logger.debug("Slack not configured for event.")
            return

    # ~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            Slack=dict(
                displayName="Slack",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="mkevenaar",
                repo="OctoPrint-Slack",
                current=self._plugin_version,

                # stable releases
                stable_branch=dict(
                    name="Stable",
                    branch="main",
                    comittish=["main"]
                ),

                # release candidates
                prerelease_branches=[
                    dict(
                        name="Development",
                        branch="devel",
                        comittish=["devel", "main"],
                    )
                ],
                # update method: pip
                pip="https://github.com/mkevenaar/OctoPrint-Slack/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Slack"
__plugin_privacypolicy__ = (
    "https://github.com/mkevenaar/OctoPrint-Slack/blob/main/PRIVACY.md"
)
__plugin_pythoncompat__ = ">=3.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    global __plugin_hooks__

    __plugin_implementation__ = SlackPlugin()

    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    }
