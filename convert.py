from email.utils import parsedate_to_datetime
from email.parser import Parser
import dateutil.relativedelta
from email import policy
import pystache
import sys
import re

def parse_res(r, keys):
	if isinstance(r, list):
		return [{k:row[i] for i,k in enumerate(keys)} for row in r]
	else:
		return {k: r[i] for i,k in enumerate(keys)}

def convert_to_markdown(file):
	with open(file) as f:
		em = Parser(policy=policy.default).parse(f)
		text = em.get_body(preferencelist=('plain')).as_string()

		date=parsedate_to_datetime(em.get('Date'))
		last_month = date - dateutil.relativedelta.relativedelta(months=1)

		re_clicks = r"(.*)\s+Clicks \(web\)"
		re_impressions = r"(.*)\s+Impressions \(web\)"
		re_url_stats = r"(?P<url>^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$)\n+(?P<num>(?:\+?[\w\.]+))"
		re_growing_queries = r"(?P<query>.*)\n+(?P<num>\+?[\d\.]+K?) clicks \((?P<device>\w+)\)"
		re_top_queries = r"(?P<query>.{6,})\n{2}(?P<num>\d+K?$)"
		re_devices = r"Desktop Mobile Tablet\s+^(?P<desktop>(?:\d|\.)+[A-Z]?) (?P<mobile>(?:\d|\.)+[A-Z]?) (?P<tablet>(?:\d|\.)+[A-Z]?)$"

		# Skip the first two matches
		re_visit_breakdown = r"(?P<country>[A-Z].*)\n+(?P<c>(?:\d|\.|K|M)+$)\s+"

		data = {
			"year": last_month.year,
			"month": last_month.month,
			'date_formatted': last_month.strftime('%B %Y'),
			'datetime': last_month,
			"clicks": re.findall(re_clicks, text)[0],
			"impressions": re.findall(re_impressions, text)[0],
			"growing_pages": parse_res(re.findall(re_url_stats, text, re.M)[1:4], ['url', 'growth']),
			"performing_pages": parse_res(re.findall(re_url_stats, text, re.M)[4:7], ['url', 'hits']),
			"growing_queries": parse_res(re.findall(re_growing_queries, text), ['query', 'growth', 'device']),
			"top_queries": parse_res(re.findall(re_top_queries, text, re.M), ['query', 'hits']),
			"device_breakdown": parse_res(re.findall(re_devices, text, re.M)[0], ['web', 'mobile', 'tablet']),
			"country_breakdown": parse_res(re.findall(re_visit_breakdown, text, re.M)[2:5], ['country', 'hits']),
			"type_breakdown": parse_res(re.findall(re_visit_breakdown, text, re.M)[-3:], ['type', 'hits'])
		}

		with open('template.mustache', 'r') as tpl:
			print(pystache.render(tpl.read(), data))

if __name__ == '__main__':
	if(len(sys.argv) >= 2):
		convert_to_markdown(sys.argv[1])
	else:
		print("Please run as python convert.py file.eml")