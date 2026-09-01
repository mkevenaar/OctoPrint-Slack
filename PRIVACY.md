# Privacy Policy

OctoPrint-Slack sends notifications only to the Slack Incoming Webhook URL configured by the OctoPrint administrator.

For enabled print events, the plugin sends the following information to Slack:

- The printed file's name
- Whether the file is stored locally or on the printer
- The elapsed print time, when supplied by OctoPrint
- The configured event message, bot username, icon, and channel override

The webhook URL and plugin settings remain in the local OctoPrint configuration. The plugin does not operate an intermediary service, collect analytics, or send data to the plugin maintainers.

Slack processes notifications according to the policies that apply to the configured Slack workspace. Administrators can stop transmission by disabling all notification events or removing the webhook URL.
