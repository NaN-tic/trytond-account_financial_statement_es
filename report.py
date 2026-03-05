# This file is part account_financial_statement_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.modules.account.common import ActivePeriodMixin
from trytond.pool import PoolMeta


class FinancialStatementTemplate(ActivePeriodMixin, metaclass=PoolMeta):
    __name__ = 'account.financial.statement.template'
