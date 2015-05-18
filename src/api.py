import os, requests

from exceptions import SlackError, SlackNo

class SlackAPI(object):

    BASE_URL = "https://slack.com/api/"

    def __init__(self, token=None, allow_env_token=True):
        if token != None:
            self.token = token
        elif allow_env_token and "SLACK_TOKEN" in os.environ:
            self.token = os.environ["SLACK_TOKEN"]
        else:
            raise SlackError("No token")
        
        self._current_target = str()

        self._channel_map = dict()
        self._group_map = dict()
        self._user_map = dict()

    def _make_request(self, method, parameters):
        url = self.BASE_URL + method
        parameters['token'] = self.token

        response = requests.post(url, data=parameters)
        
        result = response.json()
        if not result['ok']:
            raise SlackNo(result['error'])

        return result

    def __call__(self, **kwargs):
        return self.end(**kwargs)

    def end(self, **kwargs):
        target = self._current_target
        self._current_target = str()
        return self._make_request(target, kwargs)

    def __getattr__(self, target_link):
        if len(self._current_target) > 0:
            self._current_target += '.'

        self._current_target += target_link
        return self
