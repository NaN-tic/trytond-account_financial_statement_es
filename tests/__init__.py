# This file is part account_financial_statement_es module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.account_financial_statement_es.tests.test_account_financial_statement_es import suite
except ImportError:
    from .test_account_financial_statement_es import suite

__all__ = ['suite']
