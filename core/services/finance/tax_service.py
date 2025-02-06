from decimal import Decimal
from typing import Dict
from datetime import date


class TaxCalculationService:
    def __init__(self, income_service, expense_service):
        self.income_service = income_service
        self.expense_service = expense_service

        # CRA Tax Rates for BC
        self.FEDERAL_SMALL_BUSINESS_RATE = Decimal('0.09')  # 9%
        self.FEDERAL_REGULAR_RATE = Decimal('0.15')  # 15%
        self.BC_SMALL_BUSINESS_RATE = Decimal('0.02')  # 2%
        self.BC_REGULAR_RATE = Decimal('0.12')  # 12%
        self.SMALL_BUSINESS_LIMIT = Decimal('500000.00')  # $500,000

    def calculate_taxable_income(self, year: int) -> Dict[str, Decimal]:
        # Get total income for the year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        income_summary = self.income_service.get_income_summary(
            start_date=start_date,
            end_date=end_date
        )
        total_income = income_summary['total_amount']

        # Get total deductible expenses
        expense_summary = self.expense_service.get_expense_summary(
            start_date=start_date,
            end_date=end_date
        )
        total_expenses = expense_summary['total_amount']

        # Calculate taxable income
        taxable_income = total_income - total_expenses

        # Calculate taxes based on BC rates
        if taxable_income <= self.SMALL_BUSINESS_LIMIT:
            federal_tax = taxable_income * self.FEDERAL_SMALL_BUSINESS_RATE
            provincial_tax = taxable_income * self.BC_SMALL_BUSINESS_RATE
        else:
            # Split calculation for income above and below small business limit
            small_business_portion = min(taxable_income, self.SMALL_BUSINESS_LIMIT)
            regular_portion = max(Decimal('0'), taxable_income - self.SMALL_BUSINESS_LIMIT)

            federal_tax = (small_business_portion * self.FEDERAL_SMALL_BUSINESS_RATE +
                           regular_portion * self.FEDERAL_REGULAR_RATE)
            provincial_tax = (small_business_portion * self.BC_SMALL_BUSINESS_RATE +
                              regular_portion * self.BC_REGULAR_RATE)

        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'taxable_income': taxable_income,
            'federal_tax': federal_tax,
            'provincial_tax': provincial_tax,
            'total_tax': federal_tax + provincial_tax,
            'effective_tax_rate': ((federal_tax + provincial_tax) / taxable_income * 100)
            if taxable_income > 0 else Decimal('0')
        }
