import csv

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine


class bnpPlugin(Plugin):
    """Belgian BNP Paribas Fortis
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get("charset", "ISO-8859-1"))
        parser = bnpParser(f)
        parser.statement.bank_id = "BNP Paribas Fortis"
        parser.statement.currency = self.settings["currency"]
        parser.statement.account_id = self.settings["account"]
        return parser


class bnpParser(CsvStatementParser):

    date_format = "%d/%m/%Y"

    mappings = {
        'check_no': 0,
        'date': 1,
        'amount': 3,
        #'currency': 4, -- from ofxstatement 0.7.2
        'payee': 5,
        'memo': 6,
    }

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = super(bnpParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        reader = csv.reader(self.fin, delimiter=";")
        next(reader, None)
        return reader

    def fix_amount(self, amount):
        return amount.replace(',', '.')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        line[3] = self.fix_amount(line[3]) # amount
        line[6] = line[6] + " -- MSG: " + line[8] # details + memo

        stmtline = super(bnpParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'

        return stmtline
