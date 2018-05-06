#!/usr/bin/python

import argparse
import csv


class Transaction(object):
    def __init__(self, date, amount, account_number, description):
        self.date = date
        self.amount = amount
        self.description = description
        self.account_number = account_number

    def get_csv_output(self):
        return {'Date': self.date, 'Amount': self.amount,
                'AccountId': self.account_number,
                'Description': self.description,
                'Duplicator': '%s-%s' % (self.date, self.description)}

class Processor(object):

    OUTPUT_FIELDS = ['Date', 'Amount', 'AccountId', 'Description', 'Duplicator']
    CONFIG = {'CONTAINS_HEADER': True}

    def __init__(self):
        self.row_objects = []

    def process(self, bank, input_csv, account_number):
        with open(input_csv, 'rb') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for idx, row in enumerate(csv_reader):
                # skip header, if exists
                if idx == 0 and self.CONFIG['CONTAINS_HEADER']:
                    continue
                if bank == 'lloyds':
                    self.row_objects.append(self.process_lloyds_row(row, account_number))
                elif bank == 'tsb':
                    self.row_objects.append(self.process_tsb_row(row, account_number))
                elif bank == 'barclays':
                    self.row_objects.append(self.process_barclays_row(row, account_number))
                elif bank == 'halifax':
                    self.row_objects.append(self.process_halifax_row(row, account_number))
                elif bank == 'tsb-copy-paste':
                    self.row_objects.append(self.process_tsb_copy_paste(row, account_number))

    def dump(self, output_csv):
        with open(output_csv, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, self.OUTPUT_FIELDS)

            for row in self.row_objects:
                writer.writerow(row.get_csv_output())

    def process_barclays_row(self, row, account_number):
        date = row[1]
        description = row[5]
        amount = row[3]
        return Transaction(date=date, amount=amount,
                           description=description,
                           account_number=account_number)

    def process_tsb_row(self, row, account_number):
        dates = row[0].split('-')
        date = '%s/%s/%s' % (dates[2], dates[1], dates[0])
        description = row[4]
        amount = row[6] or '-%s' % row[5]
        return Transaction(date=date, amount=amount,
                           description=description,
                           account_number=account_number)

    def process_halifax_row(self, row, account_number):
        date = row[0]
        description = row[4]
        amount = row[6] or '-%s' % row[5]
        return Transaction(date=date, amount=amount,
                           description=description,
                           account_number=account_number)

    def process_lloyds_row(self, row, account_number):
        date = row[0]
        description = row[4]
        amount = row[6] or '-%s' % row[5]
        return Transaction(date=date, amount=amount,
                           description=description,
                           account_number=account_number)

    def process_tsb_copy_paste(self, row, account_number):
        date = row[0]
        description = row[1]
        amount = row[3] or '-%s' % row[4]
        return Transaction(date=date, amount=amount,
                           description=description,
                           account_number=account_number)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Bank CSV to firefly-iii input/config.')
    parser.add_argument('--bank', help='Name of bank', default='lloyds', choices=['lloyds', 'tsb-copy-paste', 'tsb', 'barclays', 'halifax'])
    parser.add_argument('--account-number', help='Bank account ID', dest='account_number', required=True)
    parser.add_argument('--input-csv', dest='input_csv', help='Input CSV filename', required=True)
    parser.add_argument('--output-csv', dest='output_csv', help='Output CSV', required=True)

    args = parser.parse_args()
    proc = Processor()
    proc.process(bank=args.bank, input_csv=args.input_csv, account_number=args.account_number)
    proc.dump(args.output_csv)
