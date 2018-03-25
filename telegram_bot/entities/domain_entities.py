import inspect
from enum import Enum, unique
import json

from telegram_bot.adsense_api.adsense_util_data_collator import DataCollator
from telegram_bot.entities.db_entities import Cron


@unique
class FlowTypes(Enum):
    DEFAULT = 0
    AVAILABLE_CRONS = 1
    NEW_CRON = 2
    REMOVE_CRON = 3
    DISABLE_CRON = 4
    ENABLE_CRON = 5
    NEXT_RUN = 6


class DialogState(object):
    def __init__(self, user_id, flow_type=FlowTypes.DEFAULT, flow_ended=False, flow_step=0):
        self.user_id = user_id
        self.flow_type = flow_type
        self.flow_ended = flow_ended
        self.flow_step = flow_step


class ReportFormatter(object):

    @staticmethod
    def format(crons):
        str = attr(Cron).__str__()
        for c in crons:
            report_params = c.request_params
            rp = ReportParams.decode(report_params)
        return str


class ReportParams(object):

    def __init__(self, **kwargs):
        self.account_id = kwargs.get('account_id', None)
        self.start_date = kwargs.get('start_date', 'today-1d')
        self.end_date = kwargs.get('end_date', 'today')
        self.currency = kwargs.get('currency', 'USD')
        self.dimension = kwargs.get('dimension', 'AD_CLIENT_ID')
        self.filter = kwargs.get('filter', None)
        self.locale = kwargs.get('locale', 'en_US')
        self.max_result = kwargs.get('max_result', None)
        self.metrics = kwargs.get('metrics', 'EARNINGS')
        self.sort = kwargs.get('sort', None)
        self.startIndex = kwargs.get('start_index', None)
        self.use_tz = kwargs.get('use_tz', None)

    def encode(self):
        return json.dumps(self.__dict__).encode()

    @staticmethod
    def decode(report_bin):
        return ReportParams(**json.loads(str(report_bin, "utf-8")))

    ## return only non default params
    def rel_complement(self):
        d = {}
        rp = ReportParams()
        for a in attr(rp):
            def_v = rp.__getattribute__(a[0])
            act_v = self.__getattribute__(a[0])
            if def_v != act_v:
                d[a[0]] = act_v
        return d


class CException(Exception):
    def __init__(self, message):
        super().__init__(message)


def attr(cls):
    attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    return [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]


def format_report(result):
    result = DataCollator([result]).collate_data()
    if not 'rows' in result or not result['rows']:
        return 'Your report is empty'
    data = {}

    for h in range(0, len(result['headers'])):
        for row in range(0, len(result['rows'])):
            header_name = result['headers'][h]['name']
            if not data.get(header_name, None):
                header = header_name
                if 'currency' in result['headers'][h]:
                    header = header_name + '(%s)' % result['headers'][h]['currency']
                data[header_name] = [header, ': ']
            data[header_name].append(result['rows'][row][h])
            data[header_name].append(', ')
    data_out = ['Report from %s to %s \n' % (result['startDate'], result['endDate'])]
    for key, val in data.items():
        del val[-1]
        val.append('\n')
        data_out.append(''.join(val))
    return ''.join(data_out)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]