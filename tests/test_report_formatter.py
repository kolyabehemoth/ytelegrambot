from telegram_bot.entities import domain_entities as de
import json


def setup_function(function):
    pass


def teardown_function(function):
    pass


def test_format_report_vs_data():
    with open('./tests/adsense_api/mocked_report.json', 'r') as file:
        result = file.read()
    data_str = de.format_report(json.loads(result))
    assert 'AD_REQUESTS: 3007' in data_str


def test_format_empty_report():
    with open('./tests/adsense_api/mocked_report2.json', 'r') as file:
        result = file.read()
    data_str = de.format_report(json.loads(result))
    assert data_str == 'Your report is empty'
    pass