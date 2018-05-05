#!/usr/bin/python

import argparse
import csv

parser = argparse.ArgumentParser(description='Convert Bank CSV to firefly-iii input/config.')
parser.add_argument('--bank', help='Name of bank', default='lloyds', choices=['lloyds', 'tsb-copy-paste', 'tsb'])
parser.add_argument('--input-csv', dest='input_csv', help='Input CSV filename', required=True)
parser.add_argument('--config', help='Config file', required=True)
parser.add_argument('--output-config', dest='output_config', help='Output firefly-iii config', required=True)
parser.add_argument('--output-csv', dest='output_csv', help='Output CSV', required=True)

args = parser.parse_args()

config = {
  'CONTAINS_HEADER': True
}

OUTPUT_FIELDS = ['Date', 'Amount', 'Description', 'Duplicator']


class Transaction(object):
    def __init__(self, date, amount, description):
        self.date = date
        self.amount = amount
        self.description = description

    def get_csv_output(self):
        return {'Date': self.date, 'Amount': self.amount,
                'Description': self.description,
                'Duplicator': '%s-%s' % (self.date, self.description)}

def process_tsb_row(row):
    dates = row[0].split('-')
    date = '%s/%s/%s' % (dates[2], dates[1], dates[0])
    description = row[4]
    amount = row[6] or '-%s' % row[5]
    return Transaction(date=date, amount=amount, description=description)


def process_lloyds_row(row):
    date = row[0]
    t_type = row[1]
    description = row[4]
    amount = row[6] or '-%s' % row[5]
    return Transaction(date=date, amount=amount, description=description)

def process_tsb_copy_paste(row):
    date = row[0]
    description = row[1]
    amount = row[3] or '-%s' % row[4]
    return Transaction(date=date, amount=amount, description=description)


row_objects = []
with open(args.input_csv, 'rb') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for idx, row in enumerate(csv_reader):
        # skip header, if exists
        if idx == 0 and config['CONTAINS_HEADER']:
            continue
        if args.bank == 'lloyds':
            row_objects.append(process_lloyds_row(row))
        elif args.bank == 'tsb':
            row_objects.append(process_tsb_row(row))
        elif args.bank == 'tsb-copy-paste':
            row_objects.append(process_tsb_copy_paste(row))



with open(args.output_csv, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, OUTPUT_FIELDS)

    for row in row_objects:
        writer.writerow(row.get_csv_output())
