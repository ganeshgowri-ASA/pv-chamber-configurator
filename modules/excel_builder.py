"""
Excel Builder Module
Utilities for creating professional Excel reports using openpyxl
"""

from openpyxl import Workbook
from openpyxl.styles import (
    Font, Alignment, Border, Side, PatternFill,
    numbers, Color
)
from openpyxl.chart import (
    BarChart, LineChart, PieChart, ScatterChart,
    Reference, Series
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd


class ExcelBuilder:
    """Professional Excel workbook builder with formatting and charts"""

    def __init__(self, output_path: str):
        """
        Initialize Excel builder

        Args:
            output_path: Path to save the Excel file
        """
        self.output_path = output_path
        self.workbook = Workbook()

        # Remove default sheet
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']

        # Define standard colors
        self.color_header = 'FF2C5AA0'  # Blue
        self.color_alt_row = 'FFE8EFF7'  # Light blue
        self.color_highlight = 'FFFFEB9C'  # Yellow
        self.color_pass = 'FFC6EFCE'  # Green
        self.color_fail = 'FFFFC7CE'  # Red

        # Define standard styles
        self._create_standard_styles()

    def _create_standard_styles(self):
        """Create standard cell styles"""
        # Header font
        self.header_font = Font(
            name='Calibri',
            size=11,
            bold=True,
            color='FFFFFFFF'
        )

        # Body font
        self.body_font = Font(
            name='Calibri',
            size=10
        )

        # Title font
        self.title_font = Font(
            name='Calibri',
            size=14,
            bold=True,
            color='FF1F4788'
        )

        # Standard border
        thin_border = Side(style='thin', color='FF000000')
        self.border = Border(
            left=thin_border,
            right=thin_border,
            top=thin_border,
            bottom=thin_border
        )

        # Alignments
        self.align_center = Alignment(horizontal='center', vertical='center')
        self.align_left = Alignment(horizontal='left', vertical='center')
        self.align_right = Alignment(horizontal='right', vertical='center')

    def create_sheet(self, sheet_name: str, index: Optional[int] = None) -> Any:
        """
        Create a new worksheet

        Args:
            sheet_name: Name for the sheet
            index: Position index (None for end)

        Returns:
            Worksheet object
        """
        if index is not None:
            sheet = self.workbook.create_sheet(sheet_name, index)
        else:
            sheet = self.workbook.create_sheet(sheet_name)
        return sheet

    def write_header_row(self, sheet: Any, headers: List[str],
                        row: int = 1, start_col: int = 1):
        """
        Write formatted header row

        Args:
            sheet: Worksheet object
            headers: List of header texts
            row: Row number (1-indexed)
            start_col: Starting column (1-indexed)
        """
        header_fill = PatternFill(
            start_color=self.color_header,
            end_color=self.color_header,
            fill_type='solid'
        )

        for i, header in enumerate(headers):
            cell = sheet.cell(row=row, column=start_col + i)
            cell.value = header
            cell.font = self.header_font
            cell.fill = header_fill
            cell.alignment = self.align_center
            cell.border = self.border

    def write_data_rows(self, sheet: Any, data: List[List[Any]],
                       start_row: int = 2, start_col: int = 1,
                       alternating_colors: bool = True):
        """
        Write data rows with optional alternating colors

        Args:
            sheet: Worksheet object
            data: List of rows (each row is a list of values)
            start_row: Starting row number
            start_col: Starting column number
            alternating_colors: Use alternating row colors
        """
        alt_fill = PatternFill(
            start_color=self.color_alt_row,
            end_color=self.color_alt_row,
            fill_type='solid'
        )

        for row_idx, row_data in enumerate(data):
            row_num = start_row + row_idx
            use_alt = alternating_colors and (row_idx % 2 == 1)

            for col_idx, value in enumerate(row_data):
                col_num = start_col + col_idx
                cell = sheet.cell(row=row_num, column=col_num)
                cell.value = value
                cell.font = self.body_font
                cell.border = self.border
                cell.alignment = self.align_left

                if use_alt:
                    cell.fill = alt_fill

    def write_dataframe(self, sheet: Any, df: pd.DataFrame,
                       start_row: int = 1, start_col: int = 1,
                       include_header: bool = True,
                       include_index: bool = False):
        """
        Write pandas DataFrame to sheet

        Args:
            sheet: Worksheet object
            df: DataFrame to write
            start_row: Starting row
            start_col: Starting column
            include_header: Write column headers
            include_index: Write index column
        """
        # Write headers
        if include_header:
            headers = list(df.columns)
            if include_index:
                headers = [df.index.name or 'Index'] + headers
            self.write_header_row(sheet, headers, start_row, start_col)
            start_row += 1

        # Write data
        data = []
        for idx, row in df.iterrows():
            row_data = list(row.values)
            if include_index:
                row_data = [idx] + row_data
            data.append(row_data)

        self.write_data_rows(sheet, data, start_row, start_col)

    def auto_fit_columns(self, sheet: Any, min_width: int = 10, max_width: int = 50):
        """
        Auto-fit column widths based on content

        Args:
            sheet: Worksheet object
            min_width: Minimum column width
            max_width: Maximum column width
        """
        for column in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    if cell.value:
                        cell_length = len(str(cell.value))
                        max_length = max(max_length, cell_length)
                except:
                    pass

            adjusted_width = min(max(max_length + 2, min_width), max_width)
            sheet.column_dimensions[column_letter].width = adjusted_width

    def freeze_panes(self, sheet: Any, row: int = 2, col: int = 1):
        """
        Freeze panes at specified position

        Args:
            sheet: Worksheet object
            row: Row to freeze after (1-indexed)
            col: Column to freeze after (1-indexed)
        """
        cell = sheet.cell(row=row, column=col)
        sheet.freeze_panes = cell.coordinate

    def add_bar_chart(self, sheet: Any, data_range: str, categories_range: str,
                     chart_position: str, title: str = "",
                     width: int = 15, height: int = 10):
        """
        Add a bar chart to the sheet

        Args:
            sheet: Worksheet object
            data_range: Range for data values (e.g., 'B2:B10')
            categories_range: Range for category labels (e.g., 'A2:A10')
            chart_position: Cell position for chart (e.g., 'E2')
            title: Chart title
            width: Chart width in cells
            height: Chart height in cells
        """
        chart = BarChart()
        chart.title = title
        chart.style = 10

        data = Reference(sheet, range_string=data_range)
        cats = Reference(sheet, range_string=categories_range)

        chart.add_data(data, titles_from_data=False)
        chart.set_categories(cats)

        chart.width = width
        chart.height = height

        sheet.add_chart(chart, chart_position)

    def add_line_chart(self, sheet: Any, data_ranges: List[str],
                      categories_range: str, chart_position: str,
                      title: str = "", series_names: Optional[List[str]] = None,
                      width: int = 15, height: int = 10):
        """
        Add a line chart to the sheet

        Args:
            sheet: Worksheet object
            data_ranges: List of data ranges (e.g., ['B2:B10', 'C2:C10'])
            categories_range: Range for X-axis labels
            chart_position: Cell position for chart
            title: Chart title
            series_names: Names for each data series
            width: Chart width
            height: Chart height
        """
        chart = LineChart()
        chart.title = title
        chart.style = 10

        cats = Reference(sheet, range_string=categories_range)

        for i, data_range in enumerate(data_ranges):
            data = Reference(sheet, range_string=data_range)
            series = Series(data, title=series_names[i] if series_names else f"Series {i+1}")
            chart.series.append(series)

        chart.set_categories(cats)
        chart.width = width
        chart.height = height

        sheet.add_chart(chart, chart_position)

    def add_pie_chart(self, sheet: Any, data_range: str, categories_range: str,
                     chart_position: str, title: str = "",
                     width: int = 15, height: int = 10):
        """
        Add a pie chart to the sheet

        Args:
            sheet: Worksheet object
            data_range: Range for data values
            categories_range: Range for category labels
            chart_position: Cell position for chart
            title: Chart title
            width: Chart width
            height: Chart height
        """
        chart = PieChart()
        chart.title = title

        data = Reference(sheet, range_string=data_range)
        cats = Reference(sheet, range_string=categories_range)

        chart.add_data(data, titles_from_data=False)
        chart.set_categories(cats)

        chart.width = width
        chart.height = height

        sheet.add_chart(chart, chart_position)

    def add_conditional_formatting(self, sheet: Any, cell_range: str,
                                   condition_type: str, value: Any = None):
        """
        Add conditional formatting to a range

        Args:
            sheet: Worksheet object
            cell_range: Range to format (e.g., 'B2:B10')
            condition_type: Type ('pass_fail', 'color_scale', 'data_bar')
            value: Threshold value (for pass_fail)
        """
        from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, DataBarRule

        if condition_type == 'pass_fail':
            # Green for values >= value, red otherwise
            pass_fill = PatternFill(start_color=self.color_pass, fill_type='solid')
            fail_fill = PatternFill(start_color=self.color_fail, fill_type='solid')

            pass_rule = CellIsRule(
                operator='greaterThanOrEqual',
                formula=[str(value)],
                fill=pass_fill
            )
            fail_rule = CellIsRule(
                operator='lessThan',
                formula=[str(value)],
                fill=fail_fill
            )

            sheet.conditional_formatting.add(cell_range, pass_rule)
            sheet.conditional_formatting.add(cell_range, fail_rule)

        elif condition_type == 'color_scale':
            rule = ColorScaleRule(
                start_type='min', start_color='FFF8696B',
                mid_type='percentile', mid_value=50, mid_color='FFFFEB84',
                end_type='max', end_color='FF63BE7B'
            )
            sheet.conditional_formatting.add(cell_range, rule)

        elif condition_type == 'data_bar':
            rule = DataBarRule(
                start_type='min', end_type='max',
                color='FF638EC6'
            )
            sheet.conditional_formatting.add(cell_range, rule)

    def add_data_validation(self, sheet: Any, cell_range: str,
                           validation_type: str, options: List[str]):
        """
        Add data validation dropdown

        Args:
            sheet: Worksheet object
            cell_range: Range to validate
            validation_type: Type ('list', 'decimal', 'whole')
            options: List of allowed values (for 'list' type)
        """
        dv = DataValidation(type=validation_type)

        if validation_type == 'list':
            dv.formula1 = f'"{",".join(options)}"'

        dv.error = 'Invalid entry'
        dv.errorTitle = 'Invalid Entry'
        dv.prompt = 'Please select from the list'
        dv.promptTitle = 'List Selection'

        sheet.add_data_validation(dv)
        dv.add(cell_range)

    def protect_sheet(self, sheet: Any, password: Optional[str] = None):
        """
        Protect worksheet

        Args:
            sheet: Worksheet object
            password: Optional password
        """
        sheet.protection.sheet = True
        if password:
            sheet.protection.password = password

    def format_as_currency(self, sheet: Any, cell_range: str, symbol: str = '₹'):
        """
        Format cells as currency

        Args:
            sheet: Worksheet object
            cell_range: Range to format
            symbol: Currency symbol
        """
        for row in sheet[cell_range]:
            for cell in row:
                cell.number_format = f'{symbol}#,##0.00'

    def format_as_percentage(self, sheet: Any, cell_range: str):
        """
        Format cells as percentage

        Args:
            sheet: Worksheet object
            cell_range: Range to format
        """
        for row in sheet[cell_range]:
            for cell in row:
                cell.number_format = numbers.FORMAT_PERCENTAGE_00

    def add_formula(self, sheet: Any, cell: str, formula: str):
        """
        Add formula to a cell

        Args:
            sheet: Worksheet object
            cell: Cell reference (e.g., 'B10')
            formula: Excel formula (without '=')
        """
        sheet[cell] = f'={formula}'

    def merge_cells(self, sheet: Any, cell_range: str):
        """
        Merge cells

        Args:
            sheet: Worksheet object
            cell_range: Range to merge (e.g., 'A1:D1')
        """
        sheet.merge_cells(cell_range)

    def add_title(self, sheet: Any, title: str, row: int = 1,
                 start_col: int = 1, span: int = 5):
        """
        Add a title to the sheet

        Args:
            sheet: Worksheet object
            title: Title text
            row: Row number
            start_col: Starting column
            span: Number of columns to span
        """
        end_col = start_col + span - 1
        cell = sheet.cell(row=row, column=start_col)
        cell.value = title
        cell.font = self.title_font
        cell.alignment = self.align_center

        # Merge cells
        start_letter = get_column_letter(start_col)
        end_letter = get_column_letter(end_col)
        sheet.merge_cells(f'{start_letter}{row}:{end_letter}{row}')

    def save(self):
        """Save the workbook to file"""
        self.workbook.save(self.output_path)
        return self.output_path


def create_workbook(output_path: str, sheet_names: List[str]) -> ExcelBuilder:
    """
    Create a new workbook with multiple sheets

    Args:
        output_path: Path to save Excel file
        sheet_names: List of sheet names to create

    Returns:
        ExcelBuilder instance
    """
    builder = ExcelBuilder(output_path)

    for i, name in enumerate(sheet_names):
        builder.create_sheet(name, i)

    return builder
