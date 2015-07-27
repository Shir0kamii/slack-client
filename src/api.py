from functools import partial

import os
import requests

from .exceptions import SlackError, SlackNo

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

        for name, api_subpart in (
                ("channels", "channels"),
                ("groups", "groups"),
                ("users", "members")):
            self._generate_caching_functions(name, api_subpart)

        for category, prefixe in (
                ("channels", "#"),
                ("groups", "#"),
                ("users", "@")):
            self._generate_id_functions(category, prefixe)

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

    def _generate_caching_functions(self, name, api_subpart):
        setattr(self, "_cache_" + name, None)

        def caching(self):
            list_channels = self._make_request(name + ".list", dict())
            serialize = lambda obj: (obj['name'], obj['id'])
            mapping = dict(map(serialize, list_channels[api_subpart]))
            setattr(self, "_cache_" + name, mapping) 
        
        method = partial(caching, self)
        setattr(self, "_caching_" + name, method)

    def _generate_id_functions(self, category, prefixe):
        cache_name = "_cache_" + category
        caching_function = getattr(self, "_caching_" + category)

        def id_function(self, name):
            if getattr(self, cache_name) is None:
                caching_function()

            to_search = name.strip(prefixe)

            if to_search in getattr(self, cache_name):
                return getattr(self, cache_name)[to_search]

        method = partial(id_function, self)
        setattr(self, category + "_id", method)
