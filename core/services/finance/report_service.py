import calendar
from decimal import Decimal
from io import BytesIO

from django.db.models import DecimalField, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class FinancialReportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_financial_report(self, report_type, start_date, end_date, queryset):
        """Main method to generate financial reports"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Build the report elements based on type
        elements = []
        elements.extend(self._build_header(report_type, start_date, end_date))

        if report_type == "income":
            elements.extend(self._build_income_report(queryset))
        elif report_type == "expense":
            elements.extend(self._build_expense_report(queryset))
        elif report_type == "taxcalculation":
            elements.extend(self._build_tax_report(queryset))

        # Generate PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _build_header(self, report_type, start_date, end_date):
        """Build report header section"""
        elements = []

        # Title
        title = f"{report_type.title()} Report"
        title_style = ParagraphStyle(
            "CustomTitle", parent=self.styles["Heading1"], fontSize=24, spaceAfter=30
        )
        elements.append(Paragraph(title, title_style))

        # Date Range
        if start_date and end_date:
            date_range = f"Period: {start_date} - {end_date}"
            elements.append(Paragraph(date_range, self.styles["Normal"]))

        elements.append(Spacer(1, 20))
        return elements

    def _build_income_report(self, queryset):
        """Build income-specific report sections"""
        elements = []

        # Income Summary
        elements.append(Paragraph("Income Summary", self.styles["Heading2"]))
        elements.append(Spacer(1, 12))

        # Calculate total income
        total_income = queryset.aggregate(
            total=Sum(
                "amount", output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )["total"] or Decimal("0.00")

        # Total Income display
        summary_table = Table(
            [["Total Income", f"${float(total_income):,.2f}"]],
            colWidths=[3 * inch, 3 * inch],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("TEXTCOLOR", (0, 0), (-1, -1), black),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Income by Client
        elements.append(Paragraph("Income by Client", self.styles["Heading3"]))
        client_data = (
            queryset.values("client__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        if client_data:
            data = [["Client", "Amount"]]
            for item in client_data:
                data.append([item["client__name"], f"${float(item['total']):,.2f}"])

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TEXTCOLOR", (0, 1), (-1, -1), black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#dddddd")),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Monthly Income Trend
        elements.append(Paragraph("Monthly Income Trend", self.styles["Heading3"]))
        monthly_data = (
            queryset.annotate(month=ExtractMonth("date"), year=ExtractYear("date"))
            .values("month", "year")
            .annotate(total=Sum("amount"))
            .order_by("year", "month")
        )

        if monthly_data:
            data = [["Month/Year", "Amount"]]
            for item in monthly_data:
                month_name = calendar.month_name[item["month"]]
                data.append(
                    [f"{month_name} {item['year']}", f"${float(item['total']):,.2f}"]
                )

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TEXTCOLOR", (0, 1), (-1, -1), black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#dddddd")),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    ]
                )
            )
            elements.append(table)

        return elements

    def _build_expense_report(self, queryset):
        """Build expense-specific report sections"""
        elements = []

        # Expense Summary
        elements.append(Paragraph("Expense Summary", self.styles["Heading2"]))
        elements.append(Spacer(1, 12))

        # Calculate total expenses
        total_expenses = queryset.aggregate(
            total=Sum(
                "amount", output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )["total"] or Decimal("0.00")

        # Total Expenses display
        summary_table = Table(
            [["Total Expenses", f"${float(total_expenses):,.2f}"]],
            colWidths=[3 * inch, 3 * inch],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("TEXTCOLOR", (0, 0), (-1, -1), black),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Expenses by Category
        elements.append(Paragraph("Expenses by Category", self.styles["Heading3"]))
        category_data = (
            queryset.values("category").annotate(total=Sum("amount")).order_by("-total")
        )

        if category_data:
            data = [["Category", "Amount"]]
            for item in category_data:
                data.append([item["category"], f"${float(item['total']):,.2f}"])

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TEXTCOLOR", (0, 1), (-1, -1), black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#dddddd")),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Expenses by Vendor
        elements.append(Paragraph("Expenses by Vendor", self.styles["Heading3"]))
        vendor_data = (
            queryset.values("vendor").annotate(total=Sum("amount")).order_by("-total")
        )

        if vendor_data:
            data = [["Vendor", "Amount"]]
            for item in vendor_data:
                vendor_name = item["vendor"] if item["vendor"] else "Unspecified"
                data.append([vendor_name, f"${float(item['total']):,.2f}"])

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TEXTCOLOR", (0, 1), (-1, -1), black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#dddddd")),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Monthly Expense Trend
        elements.append(Paragraph("Monthly Expense Trend", self.styles["Heading3"]))
        monthly_data = (
            queryset.annotate(month=ExtractMonth("date"), year=ExtractYear("date"))
            .values("month", "year")
            .annotate(total=Sum("amount"))
            .order_by("year", "month")
        )

        if monthly_data:
            data = [["Month/Year", "Amount"]]
            for item in monthly_data:
                month_name = calendar.month_name[item["month"]]
                data.append(
                    [f"{month_name} {item['year']}", f"${float(item['total']):,.2f}"]
                )

            table = Table(data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f5f5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), black),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TEXTCOLOR", (0, 1), (-1, -1), black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#dddddd")),
                        ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    ]
                )
            )
            elements.append(table)

        return elements
