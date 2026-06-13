import unittest
from datetime import date
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import create_fiscalyear
from trytond.modules.account_invoice.tests.tools import (
    set_fiscalyear_invoice_sequences,
)
from trytond.modules.account_es.tests.tools import create_chart, get_accounts
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.pool import Pool
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules
from trytond.transaction import Transaction


class TestSpanishFinancialStatementTemplates(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def create_move(self, period, amount):
        Move = Model.get('account.move', config=self.config)
        move = Move()
        move.journal = self.journal_revenue
        move.period = period
        move.date = period.start_date
        line = move.lines.new()
        line.account = self.revenue
        line.credit = amount
        line = move.lines.new()
        line.account = self.receivable
        line.party = self.party
        line.debit = amount
        move.save()
        move.click('post')

    def test(self):
        self.config = activate_modules([
                'account_financial_statement_es',
                'account_es',
                ])
        _ = create_company(config=self.config)
        company = get_company(config=self.config)
        create_chart(company=company, config=self.config)

        Party = Model.get('party.party', config=self.config)
        Journal = Model.get('account.journal', config=self.config)
        ModelData = Model.get('ir.model.data', config=self.config)
        Report = Model.get('account.financial.statement.report',
            config=self.config)
        Template = Model.get('account.financial.statement.template',
            config=self.config)

        accounts = get_accounts(company=company, config=self.config)
        self.revenue = accounts['revenue']
        self.receivable = accounts['receivable']
        self.journal_revenue, = Journal.find([('code', '=', 'REV')], limit=1)
        self.party = Party(name='Customer')
        self.party.save()

        fiscalyears = []
        for year in (2022, 2023, 2024):
            fiscalyear = create_fiscalyear(
                company=company,
                today=(date(year, 1, 1), date(year, 12, 31)),
                config=self.config)
            fiscalyear = set_fiscalyear_invoice_sequences(
                fiscalyear, config=self.config)
            fiscalyear.save()
            fiscalyear.click('create_period')
            fiscalyears.append(fiscalyear)

        for fiscalyear, amount in zip(
                fiscalyears,
                [Decimal('100'), Decimal('200'), Decimal('300')]):
            self.create_move(fiscalyear.periods[0], amount)

        template_id = ModelData.get_id(
            'account_financial_statement_es', 'es_pyg_abreviado',
            self.config.context)
        template = Template(template_id)

        report = Report()
        report.name = 'Spanish PYG'
        report.template = template
        for fiscalyear in fiscalyears:
            period = report.comparison_periods.new()
            period.fiscalyear = fiscalyear
        report.save()
        report.click('calculate')

        pool = Pool(self.config.database_name)
        ReportModel = pool.get('account.financial.statement.report')
        TemplateLineModel = pool.get('account.financial.statement.template.line')

        with Transaction().start(
                self.config.database_name, self.config.user,
                context=self.config.context):
            field_defs = TemplateLineModel.fields_get(
                ['current_value', 'previous_value'])
            self.assertEqual(
                field_defs['current_value']['string'],
                'First fiscal year formula')
            self.assertEqual(
                field_defs['previous_value']['string'],
                'Remaining fiscal years formula')

            report_record = ReportModel(report.id)
            values = {}
            for period in report_record.comparison_periods:
                result_line, = [line for line in period.lines if line.code == '49100']
                values[period.fiscalyear.id] = result_line.value
            self.assertEqual(values, {
                    fiscalyears[0].id: Decimal('100.00'),
                    fiscalyears[1].id: Decimal('200.00'),
                    fiscalyears[2].id: Decimal('300.00'),
                    })
