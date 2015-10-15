from .api import SlackObject, SlackAPI
from .exceptions import SlackNotFound

class SlackDiscussion(SlackObject):
    """
    A wrapper for Slack's channels, groups and ims

    ### Attributes

    data: nested dict containing all available informations,
    as answered by the Slack web API

    api: a SlackAPI object
    """

    def __init__(self, name, token):

        super().__init__(None, token)

        self._set_id_from_name(name)

    def __getattr__(self, name):
        """Inteface for direct access to self.data"""

        return self.data[name]


    def _try_category(self, category, name):
        """Try to initialize self, assuming the category
        
        Return True value if Initialized"""
        
        # Try getting the id
        test_id = getattr(self.api, category + '_id')(name)

        # If found
        if test_id:
            self.category = category
            self.identifiant = test_id

            return True

        return False

    def _set_id_from_name(self, name):
        """Return a channel object using its name"""

        # '@' => im 
        # '#' => channel | group
        if name.startswith('#'):
            return (self._try_category('channel', name) or 
                    self._try_category('group', name))
        elif name.startswith('@'):
            return self._try_category('im', name)
        else: # No prefix
            return (self._set_id_from_name('#' + name) or
                    self._set_id_from_name('@' + name))


    def send(self, message, **kwargs):
        """Send a message in the discussion"""

        # Default parameters for the request
        params = {
            'channel': self.identifiant,
            'text': message,
            'as_user': True
        }

        # override default parameters with keyword arguments
        params.update(kwargs)

        # Send the request using the api
        response = self.api.chat.postMessage(**params)

        # Return the timestamp of the message, allowing to change it
        return response['ts']

    def update(self, timestamp, updated_text, **kwargs):
        """Update a message"""

        params = {
            'channel': self.identifiant,
            'ts': timestamp,
            'text': updated_text,
            'as_user': True,
        }

        params.update(kwargs)

        response = self.api.chat.update(**params)

        return response['ts']

    def delete(self, timestamp):
        self.api.chat.delete(channel=self.identifiant, ts=timestamp)


    def get_history(self, **kwargs):
        return self.api.__getattr__(self.category).history(channel=self.identifiant, **kwargs)
        
