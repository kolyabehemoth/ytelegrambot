from crontab import CronTab


class User(object):

    def __init__(self, id, active=False, cron=None, chat_id=None):
        self.id = id
        self.active = active
        self.cron = cron
        self.chat_id = chat_id

    def __str__(self):
        return 'User{%s, %s, %s, %s}' % (str(self.id), str(self.chat_id), self.active, self.cron)


class Cron(object):
    def __init__(self, **kwargs):  # id, name, cron_string, request_params, active):
        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.cron_string = kwargs.get('cron_string', '* * * * *')
        self.request_params = kwargs.get('request_params', None)
        self.active = kwargs.get('active', True)
        self.user_id = kwargs.get('user_id', None)

    def __str__(self):
        rp = None if not self.request_params else self.request_params.rel_complement()
        return 'Cron {%s, %s, %s, %s, %s}' % (self.id, self.name, self.cron_string, rp, str(self.active))

    def format(self):
        rp = None if not self.request_params else self.request_params.rel_complement()
        return 'Cron name: %s \n' \
               'Cron string: %s \n' \
               'Request parameters: %s \n' \
               'Active: %s' % (self.name, self.cron_string, rp, str(self.active))

    def next_run(self):
        return CronTab(self.cron_string).next(default_utc=True)