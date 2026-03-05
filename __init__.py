# This file is part account_financial_statement_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import report


def register():
    Pool.register(
        report.FinancialStatementTemplate,
        module='account_financial_statement_es', type_='model')
