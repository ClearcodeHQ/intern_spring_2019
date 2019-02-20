import io
import csv
from collections import defaultdict
from decimal import Decimal
from datetime import datetime
import sys

import chardet
import pycountry


results = defaultdict(lambda: [0, 0])

encoding = chardet.detect(sys.stdin.buffer.peek())['encoding']
if not encoding.startswith('UTF'):
    # something might be misinterpreted as a Windows 8-bit encoding
    encoding = 'UTF-8'


for line in csv.reader(io.TextIOWrapper(sys.stdin.buffer, encoding=encoding)):
    date_string, state, imps_string, ctr_string = line
    date = str(datetime.strptime(date_string, '%m/%d/%Y').date())
    try:
        country = pycountry.subdivisions.lookup(state).country.alpha_3
    except LookupError:
        country = 'XXX'
    imps = int(imps_string)
    ctr = Decimal(ctr_string.rstrip('%')) / 100
    clicks = round(imps * ctr)
    record = results[(date, country)]
    record[0] += imps
    record[1] += clicks

with open('output.csv', 'w') as output:
    for record in sorted(results.items()):
        (date, country), (imps, clicks) = record
        output.write(f'{date},{country},{imps},{clicks}\n')
