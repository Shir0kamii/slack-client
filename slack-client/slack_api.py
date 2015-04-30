import os, requests

from slack_exceptions import *

class SlackAPI(object):
    BASE_URL = "https://slack.com/api/"

    def __init__(self, token=None, allow_env_tocken=True):
        if (token != None):
            self.token = token
        elif (allow_env_tocken and "SLACK_TOKEN" in os.environ):
            self.token = os.environ["SLACK_TOKEN"]
        else:
            raise SlackError("No token")

        self._channel_map = dict()
        self._group_map = dict()
        self._user_map = dict()

    def _make_request(self, method, parameters):
        url = SlackAPI.BASE_URL + method
        parameters['token'] = self.token

        response = requests.post(url, data=parameters)

        result = response.json()
        if not result['ok']:
            raise SlackNo(result['error'])
        return result

    def channel_id(self, channel):
        if (channel[0] == "#"):
            channel = channel[1:]

        if (channel in self._channel_map):
            return self._channel_map[channel]

        list_channels = self.channels_list()["channels"]
        self._channel_map = {x['name']: x['id'] for x in list_channels}

        if (channel in self._channel_map):
            return self._channel_map[channel]

    def group_id(self, group):
        if (group[0] == "#"):
            group = group[1:]

        if (group in self._group_map):
            return self._group_map[group]

        list_groups = self.groups_list()["groups"]
        self._group_map = {x['name']: x['id'] for x in list_groups}

        if (group in self._group_map):
            return self._group_map[group]

    def user_id(self, user):
        if (user[0] == "@"):
            user = user[1:]

        if (user in self._user_map):
            return self._user_map[user]

        list_users = self.users_list()["members"]
        self._user_map = {x["name"]: x["id"] for x in list_users}

        if (user in self._user_map):
            return self._user_map[user]

    def api_test(self, **parameters):
        return self._make_request("api.test", parameters)

    def auth_test(self):
        return self._make_request("auth.test", parameters)

    def chat_postMessage(self, channel, text, **parameters):
        parameters.update({
            'channel': channel,
            'text': text
            })
        return self._make_request("chat.postMessage", parameters)

    def chat_delete(self, channel, timestamp):
        params = {
            'channel': channel,
            'ts': timestamp
            }
        return self._make_request("chat.delete", params)

    def chat_update(self, channel, timestamp, new_text):
        params = {
            'channel': channel,
            'ts': timestamp,
            'text': new_text
        }
        return self._make_request("chat.update", params)

    def channels_archive(self, channel):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel
        }
        return self._make_request("channels.archive", params)

    def channels_create(self, name):
        params = {
            'name': name
        }
        return self._make_request("channels.create", params)

    def channels_history(self, channel, **parameters):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        parameters.update({
            'channel': channel
        })
        return self._make_request("channels.history", parameters)

    def channels_info(self, channel):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel
        }
        return self._make_request("channels.info", params)

    def channels_invite(self, channel, user):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        if (user.startswith("@")):
            user = self.user_id(user)
        params = {
            'channel': channel,
            'user': user
        }
        return self._make_request("channels.invite", params)

    def channels_join(self, name):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'name': name
        }
        return self._make_request("channels.join", params)

    def channels_kick(self, channel, user):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel,
            'user': user
        }
        return self._make_request("channels.kick", params)

    def channels_leave(self, channel, user):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel
        }
        return self._make_request("channels.leave", params)

    def channels_list(self, exclude_archived=True):
        params = {
            'exclude_archived': int(exclude_archived)
        }
        return self._make_request("channels.list", params)

    def channels_mark(self, channel, timestamp):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel,
            'ts': timestamp
        }
        return self._make_request("channels.mark", params)

    def channels_rename(self, channel, name):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel,
            'name': name
        }
        return self._make_request("channels.rename", params)

    def channels_setPurpose(self, channel, purpose):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel,
            'purpose': purpose
        }
        return self._make_request("channels.setPurpose", params)

    def channels_setTopic(self, channel, topic):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel,
            'topic': topic
        }
        return self._make_request("channels.setTopic", params)

    def channels_unarchive(self, channel):
        if (channel.startswith("#")):
            channel = self.channel_id(channel)
        params = {
            'channel': channel
        }
        return self._make_request("channels.unarchive", params)

    def emoji_list(self):
        return self._make_request("emoji.list", dict())

    def files_delete(self, fileId):
        params = {
            'file': fileId
        }
        return self._make_request("files.delete", params)

    def files_info(self, fileId, **parameters):
        parameters.update({
            'file': fileId
        })
        return self._make_request("files.info", parameters)

    def files_list(self, **parameters):
        return self._make_request("files.list", parameters)

    def files_upload(self, **parameters):
        return self._make_request("files.upload", parameters)

    def groups_archive(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.archive", params)

    def groups_close(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.close", params)

    def groups_create(self, name):
        params = {
            'name': name
        }
        return self._make_request("groups.create", params)

    def groups_createChild(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.createChild", params)

    def groups_archive(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.archive", params)

    def groups_history(self, group, **parameters):
        if (group.startswith("#")):
            group = self.group_id(group)
        parameters.update({
            'channel': channel
        })
        return self._make_request("groups.history", parameters)

    def groups_info(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.info", params)

    def groups_invite(self, group, user):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'user': user
        }
        return self._make_request("groups.invite", params)

    def groups_kick(self, group, user):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'user': user
        }
        return self._make_request("groups.kick", params)

    def groups_leave(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.leave", params)

    def groups_list(self, exclude_archived=True):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'exclude_archived': int(exclude_archived)
        }
        return self._make_request("groups.list", params)

    def groups_mark(self, group, timestamp):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'ts': timestamp
        }
        return self._make_request("groups.mark", params)

    def group_open(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.open", params)

    def groups_rename(self, group, name):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'name': name
        }
        return self._make_request("groups.rename", params)

    def groups_setPurpose(self, group, purpose):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'purpose': purpose
        }
        return self._make_request("groups.setPurpose", params)

    def groups_setTopic(self, group, topic):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel,
            'topic': topic
        }
        return self._make_request("groups.setTopic", params)

    def groups_unarchive(self, group):
        if (group.startswith("#")):
            group = self.group_id(group)
        params = {
            'channel': channel
        }
        return self._make_request("groups.unarchive", params)

    def im_close(self, channel):
        params = {
            'channel': channel
        }
        return self._make_request("im.close", params)

    def im_history(self, channel, **parameters):
        parameters.update({
            'channel': channel
        })
        return self._make_request("im.history", parameters)

    def im_list(self):
        return self._make_request("im.list", dict())

    def im_mark(self, channel, timestamp):
        params = {
            'channel': channel,
            'ts': timestamp
        }
        return self._make_resquest("im.mark", params)

    def im_close(self, channel):
        params = {
            'channel': channel
        }
        return self._make_request("im.close", params)

    def oauth_access(self):
        pass

    def rtm_start(self):
        return self._make_request("rtm.start", dict())

    def search_all(self, query, **parameters):
        parameters.update({
            'query': query
        })
        return self._make_request("search.all", parameters)

    def search_file(self, query, **parameters):
        parameters.update({
            'query': query
        })
        return self._make_request("search.file", parameters)

    def search_message(self, query, **parameters):
        parameters.update({
            'query': query
        })
        return self._make_request("search.message", parameters)

    def stars_list(self, **parameters):
        return self._make_request("stars.list", parameters)

    def team_accessLog(self, **parameters):
        return self._make_request("team.accessLog", parameters)

    def team_info(self):
        return self._make_request("team.info", dict())

    def users_getPresence(self, user):
        if (user.startswith("@")):
            user = self.user_id(user)
        parameters = {
            'user': user
        }
        return self._make_request("users.getPresence", parameters)

    def users_info(self, user):
        if (user.startswith("@")):
            user = self.user_id(user)
        parameters = {
            'user': user
        }
        return self._make_request("users.info", parameters)

    def users_list(self):
        return self._make_request("users.list", dict())

    def users_setActive(self):
        return self._make_request("users.setActive", dict())

    def users_setPresence(self, presence):
        parameters = {
            'presence': presence
        }
        return self._make_request("users.setPresence", parameters)
