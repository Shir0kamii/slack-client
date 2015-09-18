import os
import requests

from .exceptions import SlackError, SlackNo, SlackMissingAPI

class SlackObject:
    """The base object for all Slack Objects
    
    ### Attributes

    identifiant: UID of the object (unique within a domain name)
    api: A SlackAPI object
    """

    _MAP_OBJECTS = dict()

    def __init__(self, identifiant, token=None):
        """initialize a way to identify each instance
        
        identifiant: The unique ID of the object
        
        token: Either a token string or a SlackAPI object
        can be None only in a SlackAPI initialization
        """

        self.identifiant = identifiant
        self._MAP_OBJECTS[identifiant] = self

        # self.api must be a SlackAPI object
        # If self is a SlackAPI object, self.api doesn't matter
        # If the token is a SlackAPI object, use it as api interface
        # If the token is a string, make a SlackAPI instance out of it
        # Else, an exception is raised
        if isinstance(token, SlackAPI) or isinstance(self, SlackAPI):
            self.api = token
        elif isinstance(token, str):
            self.api = SlackAPI.get_object(token)
        else:
            raise SlackMissingAPI

    @classmethod
    def get_instance(cls, identifiant, token=None):
        """Return an instance of a class based on its identifiant
        
        It returns the same object if called with the same identifiant
        """

        if identifiant in cls._MAP_OBJECTS:
            return cls._MAP_OBJECTS[identifiant]
        else:
            return cls(token, identifiant)

class SlackAPI(SlackObject):
    """Main class for manipulation of the API

    Stands as a wrapper for a single token

    ### Attributes

    #### Class attributes

    BASE_URL: The base url of the web slack api

    #### Public instance attributes

    token: token for the Slack web API

    #### Private instance attributes

    _cache_channels: a cache for conversion from name to channel
    
    _cache_groups: a cache for conversion from name to group
    
    _cache_users: a cache for conversion from name to user
    
    _cache_ims: a cache for conversion from user to im

    ### Public API

    group_id: Return the id of the group, or None if not found
    
    users_id: Return the id of the users, or None if not found
    
    channel_id: Return the id of the channel, or None if not found

    im_id: Return the id of the im, or None if not found
    
    ### Private API

    _caching_channels: A method to cache channels
    
    _caching_groups: A method to cache groups
    
    _caching_users: A method to cache users
    
    _caching_ims: A method to cache ims

    _userid_to_imid: Conversion from userid to imid
    """


    ######## Class attributes #############


    BASE_URL = "https://slack.com/api/"


    ########## Magix methods ############


    def __init__(self, token=None, allow_env_token=False):
        """Give you a Wrapper for a token
        
        The token can be either given through parameter "token"
        or be read from the environment (when allow_env_token is True)
        """

        # Init the object
        super().__init__(token)

        # Try to find a token
        if token != None:
            self.token = token
        elif allow_env_token and "SLACK_TOKEN" in os.environ:
            self.token = os.environ["SLACK_TOKEN"]
        else:
            raise SlackError("No token")

        # Init caches to None, for them not to be cached by __getattr__
        for category in ('channels', 'groups', 'users', 'ims'):
            setattr(self, '_cache_' + category, None)
        
        self._current_target = str()
        
    def __call__(self, **kwargs):
        """Allow users to call API in the form `api.channels.list()`"""

        target = self._current_target

        # Clean the current target
        self._current_target = str()

        return self._make_request(target, kwargs)


    def __getattr__(self, target_link):
        """Allow to call API in fashion way

        It permits to do `api.channels.list()` to call channels.list method"""

        if len(self._current_target) > 0:
            self._current_target += '.'

        self._current_target += target_link
        return self


    ######## Private API #############
    # Generated methods :
    # _caching_channels()
    # _caching_groups()
    # _cahcing_users()


    def _make_request(self, method, parameters):
        """Send a request to the Slack web API"""

        # Make url
        url = self.BASE_URL + method

        # Integrate the token in the request and post it
        parameters['token'] = self.token
        response = requests.post(url, data=parameters)

        # Parse the response, searching for error
        result = response.json()
        if not result['ok']:
            raise SlackNo(result['error'], result)

        return result


    @classmethod
    def _generate_caching_methods(cls, name, api_subpart):
        """Special method generating the caching methods
        
        Deleted after use"""

        method_name = "_caching_" + name

        def caching(self):
            """set later"""

            # Get the list of objects 
            list_objects = self._make_request(name + ".list", dict())

            # Fonction to format each object in tuple (<name>, <id>)
            serialize = lambda obj: (obj['name'], obj['id'])

            # Use the fonction on each objects
            mapping = dict(map(serialize, list_objects[api_subpart]))

            # Set the cache
            setattr(self, "_cache_" + name, mapping) 
        
        # Meta attributes of the function
        caching.__doc__ = "Cache {name} in _cache_{name}".format(name=name)
        caching.__name__ = method_name

        # Integrate the caching method in the class
        setattr(cls, method_name, caching)


    @classmethod
    def _generate_id_methods(cls, category, prefix):
        """Special method generating id methods
        
        Deleted after use"""

        # Make some preprocessing outside of the generated method
        cache_name = "_cache_" + category
        caching_method = getattr(cls, "_caching_" + category)

        def id_method(self, name):
            """set later"""

            # If the cache doesn't exist, create it
            if getattr(self, cache_name) is None:
                caching_method(self)

            # Remove the prefix if present
            to_search = name.strip(prefix)

            # Search the object in the cache and return it
            # If nothing is found, return None
            if to_search in getattr(self, cache_name):
                return getattr(self, cache_name)[to_search]

        id_method.__doc__ = "Retrieve {category}'s ID".format(
                category=category[:-1]) # Quick hack to remove the trailing s
        id_method.__name__ = "{category}_id".format(category=category)

        setattr(cls, category[:-1] + "_id", id_method)

    def _caching_ims(self):
        """Cache ims in _cache_ims"""

        # Get the list of objects 
        list_objects = self._make_request("im.list", dict())

        # Fonction to format each object in tuple (<name>, <id>)
        serialize = lambda obj: (obj['user'], obj['id'])

        # Use the fonction on each objects
        mapping = dict(map(serialize, list_objects['ims']))

        # Set the cache
        self._cache_ims = mapping


    def _userid_to_imid(self, userid):
        """Return the im corresponding to the user"""

        # If the cache doesn't exist, create it
        if getattr(self, '_cache_im') is None:
            self._caching_ims()

        if userid in self._cache_ims:
            return self._cache_ims[userid]


    ######### Public API ###############


    def im_id(self, name):
        """Retrive im'id corresponding to username"""
        
        # If the cache doesn't exist, create it
        if getattr(self, '_cache_ims') is None:
            self._caching_ims()

        # Convert name to userid
        to_search = self.user_id(name)

        # Search the object in the cache and return it
        # If nothing is found, return None
        if to_search in self._cache_ims:
            return self._cache_ims[to_search]


# Generate caching methods
for name, api_subpart in (
        ("channels", "channels"),
        ("groups", "groups"),
        ("users", "members"),
        ):
    SlackAPI._generate_caching_methods(name, api_subpart)

del SlackAPI._generate_caching_methods


# Generate IDs methods
for category, prefix in (
        ("channels", "#"),
        ("groups", "#"),
        ("users", "@"),
        ):
    SlackAPI._generate_id_methods(category, prefix)

del SlackAPI._generate_id_methods
