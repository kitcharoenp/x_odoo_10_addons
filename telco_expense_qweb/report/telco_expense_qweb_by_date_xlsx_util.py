# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
import io

import xlsxwriter

OTHER_COLUMN_KEY = (None, 'อื่นๆ')


def _get_gl_columns(project_data):
    columns = []
    seen = set()
    for exp in project_data:
        code = exp['code']
        key = (code, exp['product_name']) if code else OTHER_COLUMN_KEY
        if key not in seen:
            seen.add(key)
            columns.append(key)
    return columns


def _write_project_sheet(workbook, formats, project_name, project_data):
    sheet_name = (project_name or 'Sheet')[:31]
    sheet = workbook.add_worksheet(sheet_name)
    gl_columns = _get_gl_columns(project_data)

    header_row = 0
    code_row = 1
    col_row = 2
    first_data_row = 3

    fixed_headers = ['ลำดับ', 'วันที่เอกสาร', 'รวม']
    for col, label in enumerate(fixed_headers):
        sheet.merge_range(
            header_row, col, col_row, col, label, formats['header'])

    gl_col_start = len(fixed_headers)
    for i, (code, name) in enumerate(gl_columns):
        col = gl_col_start + i
        sheet.write(header_row, col, name, formats['header'])
        sheet.write(code_row, col, code or '', formats['header'])

    require_po_col = gl_col_start + len(gl_columns)
    sheet.merge_range(
        header_row, require_po_col, col_row, require_po_col,
        'Require PO (Y/N)', formats['header'])

    totals = [0.0] * len(gl_columns)
    row = first_data_row
    for i, exp in enumerate(project_data, start=1):
        sheet.write(row, 0, i)
        sheet.write(row, 1, exp['date'].strftime('%d-%m-%Y'))
        sheet.write(row, 2, exp['total_amount'], formats['amount'])

        code = exp['code']
        key = (code, exp['product_name']) if code else OTHER_COLUMN_KEY
        col_index = gl_columns.index(key)
        sheet.write(
            row, gl_col_start + col_index,
            exp['total_amount'], formats['amount'])
        totals[col_index] += exp['total_amount']

        sheet.write(
            row, require_po_col,
            'Y' if exp['require_po'] else 'N')
        row += 1

    total_row = row
    sheet.write(total_row, 1, 'รวมยอด', formats['bold'])
    sheet.write(
        total_row, 2, sum(exp['total_amount'] for exp in project_data),
        formats['bold_amount'])
    for i, total in enumerate(totals):
        sheet.write(total_row, gl_col_start + i, total, formats['bold_amount'])

    summary_row = total_row + 2
    sheet.write(summary_row, 2, 'GL Account', formats['bold'])
    sheet.write(summary_row, 3, 'GL Account NO.', formats['bold'])
    sheet.write(summary_row, 4, 'Amount', formats['bold'])
    summary_row += 1
    for (code, name), total in zip(gl_columns, totals):
        sheet.write(summary_row, 2, name)
        sheet.write(summary_row, 3, code or '')
        sheet.write(summary_row, 4, total, formats['amount'])
        summary_row += 1

    no_po_total = sum(
        exp['total_amount'] for exp in project_data if not exp['require_po'])
    po_total = sum(
        exp['total_amount'] for exp in project_data if exp['require_po'])

    summary_row += 1
    sheet.write(summary_row, 2, 'คชจ.ตั้งตรงไม่มี PO')
    sheet.write(summary_row, 4, no_po_total, formats['amount'])
    summary_row += 1
    sheet.write(summary_row, 2, 'คชจ. ที่มี PO')
    sheet.write(summary_row, 4, po_total, formats['amount'])
    summary_row += 1
    sheet.write(summary_row, 2, 'รวม', formats['bold'])
    sheet.write(
        summary_row, 4, no_po_total + po_total, formats['bold_amount'])

    sheet.set_column(0, 1, 12)
    sheet.set_column(2, require_po_col, 16)


def build_xlsx(data_by_project):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    formats = {
        'header': workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#D9D9D9', 'border': 1, 'text_wrap': True}),
        'bold': workbook.add_format({'bold': True}),
        'amount': workbook.add_format({'num_format': '#,##0.00'}),
        'bold_amount': workbook.add_format({
            'bold': True, 'num_format': '#,##0.00'}),
    }
    for obj in data_by_project:
        _write_project_sheet(
            workbook, formats, obj['project_name'], obj['data'])
    workbook.close()
    return output.getvalue()
