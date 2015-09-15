from .api import SlackObject, SlackAPI

class SlackChannel(SlackObject):
    """
    A wrapper for Slack's channels

    ### Attributes

    data: nested dict containing all available informations,
    as answered by the Slack web API

    api: a SlackAPI object
    """

    def __init__(self, id, token):

        super().__init__(id, token)

        # Call channels.info to get informations
        self.data = self.api.channels.info(channel=id)['channel']

    def __getattr__(self, name):
        """Inteface for direct access to self.data"""

        return self.data[name]

    @classmethod
    def from_name(cls, token, name):
        """Return a channel object using its name"""

        if isinstance(token, SlackAPI):
            api = token
        elif isinstance(token, string):
            api = SlackAPI.get_object(token)
        else:
            raise TypeError

        return cls(api, api.channels_id(name))

    def send(self, message, **kwargs):
        """Send a message on the channel"""

        # Default parameters for the request
        params = {
            'channel': self.identifiant,
            'text': message,
            'as_user': True
        }

        # override default parameters with keyword arguments
        params.update(kwargs)

        # Send the request using the api
        self.api.chat.postMessage(**params)
