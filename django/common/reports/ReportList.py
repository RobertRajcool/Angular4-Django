from django.http import HttpResponse
import csv
from collections import OrderedDict
from wkhtmltopdf.views import PDFTemplateResponse
from openpyxl import Workbook
from common.reports.ReportFieldMapping import ReportFieldMapping


class ReportList:
    def export(self, data_list, screen_name, export_type='csv', report_name=None):
        """ Converting given queryset into file content """

        report_filed_mapper = ReportFieldMapping()
        report_filed_mappings = report_filed_mapper.createReport(hash_key_value=report_name)

        if export_type == 'csv':
            return self.exportCSVFile(queryset=data_list,
                                      screename=screen_name,
                                      extraoptions=report_filed_mappings)
        if export_type == 'pdf':
            return self.exportPDFFile(queryset=data_list,
                                      screename=screen_name,
                                      extraoptions=report_filed_mappings)
        if export_type == 'xlsx':
            return self.exportEXCELFile(data_list=data_list,
                                        screen_name=screen_name,
                                        field_mappings=report_filed_mappings)

    def exportCSVFile(self, queryset, extraoptions, screename):
        filename = screename + '.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        writer = csv.writer(response)
        field_names = [field for field in extraoptions]
        field_label = [extraoptions[field] for field in extraoptions]
        # Write a first row with header information
        writer.writerow(field_label)
        # Write data rows
        for obj in queryset:
            rowvalue = []
            for field in field_names:
                if field in obj:
                    objectvalue = obj[field]
                    rowvalue.append(objectvalue)
                else:
                    rowvalue.append('')
            writer.writerow(rowvalue)
        return response


    def exportPDFFile(self, request, queryset, extraoptions, screename):

        template_data = {'screenName': screename,
                         'tableheaders': extraoptions,
                         'tablebodycontent': queryset
                         }
        file_name = screename + '.pdf'
        pdf_response = PDFTemplateResponse(
            request=request,
            template='red-pdf-list.html',
            filename=file_name,
            context=template_data,
            cmd_options={
                'load-error-handling': 'ignore',
                'title': screename,
                'orientation': 'Landscape',
                'footer-center': 'Page [page] of [topage]',
                'print-media-type': True

            }
        )
        return pdf_response

    def exportEXCELFile(self, data_list, screen_name, field_mappings=None):
        """ Creating excel file response """

        file_name = screen_name + '.xlsx'
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response['FILE_NAME'] = file_name
        data_list = list(data_list)

        wb = Workbook()
        ws = wb.active
        ws.title = screen_name

        if len(data_list) > 0:
            fields = list(data_list[0].keys())

            if field_mappings:
                fields = list(field_mappings.values())

            # Write a first row with header information
            ws.append(fields)

            # Write data rows
            for row in data_list:
                data_to_write = row

                if field_mappings:
                    data_to_write = OrderedDict([(value, row[key]) for key, value in field_mappings.items()])

                ws.append(list(data_to_write.values()))

        wb.save(response)
        return response
