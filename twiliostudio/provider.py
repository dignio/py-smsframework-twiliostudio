import json
import requests

from smsframework import IProvider, exc

from . import error

EXECUTIONS_URL = "https://studio.twilio.com/v1/Flows/{}/Executions"


class TwilioStudioProvider(IProvider):
    """ Twilio Studio provider """

    def __init__(self, gateway, name, account_sid=None, secret=None, username=None):
        """ Configure Twilio Studio provider

        """
        self.account_sid = account_sid
        self.username = username
        self.secret = secret
        super(TwilioStudioProvider, self).__init__(gateway, name)

    def send(self, message):
        """ Send a message

            :type message: smsframework.data.OutgoingMessage.OutgoingMessage
            :rtype: OutgoingMessage
            """

        # Twilio Studio requires the parameters From and To, and an optional json-formatted string
        # with extra parameters.
        twilio_format = "+{}".format
        params = dict(
            From=twilio_format(message.src),
            To=twilio_format(message.dst),
            Parameters=json.dumps(message.provider_params),
        )

        # Send
        try:
            response = requests.post(
                url=EXECUTIONS_URL.format(self.account_sid),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
                },
                auth=(self.username, self.secret),
                data=params,
            )
            response.raise_for_status()

            body = response.json()
            # body['url'] ~= 'https://studio.twilio.com/v1/Flows/sid/Executions/FN0000'
            message.msgid = '/'.join(body['url'].rsplit('/', 4)[1:])
            return message
        except requests.exceptions.RequestException as e:
            raise error.TwilioStudioProviderError(e.code, str(e))

    # region Public


# endregion
