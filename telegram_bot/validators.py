import abc
import logging
import re
from crontab import CronTab
from telegram_bot.entities.domain_entities import CException
from datetime import datetime
from money import Money

logger = logging.getLogger(__name__)


# TODO: implement the rest of validators
class Validator(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def validate(self, message):
        raise NotImplementedError('U stupied shit should implement validate method')


class CronNameValidator(Validator):
    field_name = 'name'
    name_regex = re.compile(r'[A-Za-z0-9_]{,16}')

    def validate(self, message):
        logger.debug('CronNameValidator')
        if len(message) > 16:
            raise CException('Cron name should be less than 16 character, bruh')
        if not self.name_regex.match(message):
            raise CException('Cron name should contain only en characters and underscore')
        return self.field_name, message


class CronStringValidator(Validator):
    field_name = 'cron_string'

    def validate(self, message):
        logger.debug('CronStringValidator')
        try:
            cron = CronTab(message)
        except ValueError as e:
            raise CException(e)
        return self.field_name, message


class AccountIdValidator(Validator):
    field_name = 'account_id'
    account_id_regex = re.compile('pub-\d{16}')

    def validate(self, message):
        logger.debug('AccountIdValidator')
        if not self.account_id_regex.match(message):
            raise CException('Adsense account id is wrong, check pls it correctness')
        return self.field_name, message


class StartDateValidator(Validator):
    field_name = 'start_date'
    date_format = '%Y-%m-%d'
    today_const = 'today'
    #google regex = \d{4}-\d{2}-\d{2}|(today|startOfMonth|startOfYear)(([\-\+]\d+[dwmy]){0,3}?)|(latest-(\d{2})-(\d{2})(-\d+y)?)|(latest-latest-(\d{2})(-\d+m)?)


    def validate(self, message):
        logger.debug('StartDateValidator')
        if not message == self.today_const:
            try:
                date = datetime.strftime(message, self.date_format)
            except ValueError as e:
                raise CException('Your start date is in the wrong format. Allowed values today or YYYY-MM-DD')
        return self.field_name, message


class EndDateValidator(Validator):
    field_name = 'end_date'
    date_format = '%Y-%m-%d'
    today_const = 'today'

    def validate(self, message):
        logger.debug('EndDateValidator')
        return self.field_name, None


class CurrencyValidator(Validator):
    field_name = 'currency'

    def validate(self, message):
        logger.debug('CurrencyValidator')
        return self.field_name, None


class DimensionValidator(Validator):
    acceptable_values = ['AD_CLIENT_ID', 'AD_FORMAT_CODE', 'AD_FORMAT_NAME', 'AD_UNIT_CODE', 'AD_UNIT_ID', 'AD_UNIT_NAME',
                         'AD_UNIT_SIZE_CODE', 'AD_UNIT_SIZE_NAME', 'BID_TYPE_CODE', 'BID_TYPE_NAME', 'BUYER_NETWORK_ID',
                         'BUYER_NETWORK_NAME', 'COUNTRY_CODE', 'COUNTRY_NAME', 'CUSTOM_CHANNEL_CODE', 'CUSTOM_CHANNEL_ID',
                         'CUSTOM_CHANNEL_NAME', 'DATE', 'DOMAIN_NAME', 'MONTH', 'PLATFORM_TYPE_CODE', 'PLATFORM_TYPE_NAME',
                         'PRODUCT_CODE', 'PRODUCT_NAME', 'TARGETING_TYPE_CODE', 'TARGETING_TYPE_NAME', 'URL_CHANNEL_ID',
                         'URL_CHANNEL_NAME', 'WEEK']
    field_name = 'dimension'

    def validate(self, message):
        logger.debug('DimensionValidator')
        n_m = message.replace(' ', '_')
        n_m = n_m.upper()
        if n_m not in self.acceptable_values:
            raise CException('Wrong type of dimension. Allowed dimensions are: %s' % self.acceptable_values)

        return self.field_name, None


class FilterValidator(Validator):
    field_name = 'filter'

    def validate(self, message):
        logger.debug('FilterValidator')
        return self.field_name, None


class LocaleValidator(Validator):
    acceptable_values = ['en_US']
    field_name = 'locale'

    def validate(self, message):
        logger.debug('LocaleValidator')
        return self.field_name, self.acceptable_values[0]


class MetricValidator(Validator):
    acceptable_values = ['AD_REQUESTS', 'AD_REQUESTS_COVERAGE', 'AD_REQUESTS_CTR', 'AD_REQUESTS_RPM', 'CLICKS',
                         'COST_PER_CLICK', 'EARNINGS', 'INDIVIDUAL_AD_IMPRESSIONS', 'INDIVIDUAL_AD_IMPRESSIONS_CTR',
                         'INDIVIDUAL_AD_IMPRESSIONS_RPM', 'MATCHED_AD_REQUESTS', 'MATCHED_AD_REQUESTS_CTR',
                         'MATCHED_AD_REQUESTS_RPM', 'PAGE_VIEWS', 'PAGE_VIEWS_CTR', 'PAGE_VIEWS_RPM']
    field_name = 'metric'

    def validate(self, message):
        logger.debug('MetricValidator')
        n_m = message.replace(' ', '_')
        n_m = n_m.upper()
        if n_m not in self.acceptable_values:
            raise CException('Wrong type of metric. Allowed metrics are: %s' % self.acceptable_values)
        return self.field_name, n_m


class SortValidator(Validator):
    acceptable_values = MetricValidator.acceptable_values + DimensionValidator.acceptable_values
    field_name = 'sort'

    def validate(self, message):
        logger.debug('CronNameValidator')
        n_m = message.replace(' ', '_')
        n_m = n_m.upper()
        if n_m not in self.acceptable_values:
            raise CException('Wrong type of metric. Allowed metrics are: %s' % self.acceptable_values)
        return self.field_name, n_m


class MaxResultValidator(Validator):
    field_name = 'max_result'
    max_result_const = 50000

    def validate(self, message):
        logger.debug('MaxResultValidator')
        try:
            max_row = int(message)
            if max_row > self.max_result_const:
                raise CException('MaxResult should be in range from 0 to %s' % self.max_result_const)
        except ValueError:
            raise CException('MaxResult should be in range from 0 to %s' % self.max_result_const)
        return self.field_name, None
