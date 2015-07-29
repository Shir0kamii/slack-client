from functools import partial

import os
import requests

from .exceptions import SlackError, SlackNo

class SlackAPI(object):
    """Main class for manipulation of the API

    Stands as a wrapper for a single token"""

    BASE_URL = "https://slack.com/api/"

    def __init__(self, token=None, allow_env_token=False):
        if token != None:
            self.token = token
        elif allow_env_token and "SLACK_TOKEN" in os.environ:
            self.token = os.environ["SLACK_TOKEN"]
        else:
            raise SlackError("No token")
        
        self._current_target = str()

        for cache_category in (
                "channels",
                "groups",
                "users"):
            setattr(self, "_cache_" + cache_category, None)

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

    @classmethod
    def _generate_caching_methods(cls, name, api_subpart):

        def caching(self):
            list_channels = self._make_request(name + ".list", dict())
            serialize = lambda obj: (obj['name'], obj['id'])
            mapping = dict(map(serialize, list_channels[api_subpart]))
            setattr(self, "_cache_" + name, mapping) 
        
        setattr(cls, "_caching_" + name, caching)
    
    @classmethod
    def _generate_id_methods(cls, category, prefix):
        cache_name = "_cache_" + category
        caching_method = getattr(cls, "_caching_" + category)

        def id_method(self, name):
            if getattr(self, cache_name) is None:
                caching_method(self)

            to_search = name.strip(prefix)

            if to_search in getattr(self, cache_name):
                return getattr(self, cache_name)[to_search]

        setattr(cls, category + "_id", id_method)
    
for name, api_subpart in (
        ("channels", "channels"),
        ("groups", "groups"),
        ("users", "members")):
    SlackAPI._generate_caching_methods(name, api_subpart)

for category, prefix in (
        ("channels", "#"),
        ("groups", "#"),
        ("users", "@")):
    SlackAPI._generate_id_methods(category, prefix)

