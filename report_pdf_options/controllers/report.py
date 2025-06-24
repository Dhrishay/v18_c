from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.report import ReportController
import json
from werkzeug import urls


class CustomReportController(ReportController):

     # @http.route(
     #      [
     #           "/report/<converter>/<reportname>",
     #           "/report/<converter>/<reportname>/<docids>",
     #      ],
     #      type="http",
     #      auth="user",
     #      website=True,
     # )
     # def report_routes(self, reportname, docids=None, converter=None, **data):
     #      print("\n\n\nreport_routes-------------custom-----------------------------")
     #      if converter != "pdf":
     #           return super().report_routes(reportname, docids=docids, converter=converter, **data)
     #
     #      report_obj = request.env["ir.actions.report"]
     #      report = report_obj._get_report_from_name(reportname)
     #      context = dict(request.env.context)
     #      # print("data--------------------------------",data)
     #
          # # ----------- Handle Options (JSON string) ------------
          # if "options" in data:
          #      print("if1111111111111")
          #      try:
          #           print("try---------------------")
          #           options_json = urls.url_unquote_plus(data.pop("options"))
          #           options = json.loads(options_json)
          #           data.update(options)
          #           print("data-----1111------------------",data)
          #      except Exception as e:
          #           print("exception----------------------")
          #           return request.make_response(f"Invalid options: {str(e)}", [('Content-Type', 'text/plain')])
          #
          # # ----------- Handle Context (JSON string) ------------
          # if "context" in data:
          #      print("if 22222222222222222")
          #      try:
          #           print("try---------------------")
          #           context_json = urls.url_unquote_plus(data["context"])
          #           context.update(json.loads(context_json))
          #           print("context-------------------",context)
          #      except Exception as e:
          #           print("exception----------------------")
          #           return request.make_response(f"Invalid context: {str(e)}", [('Content-Type', 'text/plain')])

     #      # Set company context
     #      if "cid" in data:
     #           try:
     #                company_ids = [int(cid) for cid in data["cid"].split(",")]
     #                context["allowed_company_ids"] = company_ids
     #           except:
     #                pass
     #
     #      request.env.context = context
     #      print("context----------------------------------",context)
     #
     #      if 'allowed_company_ids' in context:
     #           print("if---------------------")
     #           company_id = request.env['res.users'].sudo().browse(int(context['allowed_company_ids'][0]))
     #           print("company_id-----------------------------",company_id)
     #      else:
     #           company_id = request.env.company
     #           print("company_id--------------------------",company_id)
     #
     #      # Doc IDs (if any)
     #      if docids:
     #           docids = [int(i) for i in docids.split(",")]
     #           model = report.model
     #           records = request.env[model].browse(docids)
     #           records.check_access_rule("read")
     #
     #      report = report.with_company(company_id)
     #      pdf = report.with_context(**context)._render_qweb_pdf(reportname, docids, data=data)[0]
     #      pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
     #      return request.make_response(pdf, headers=pdfhttpheaders)

          # Render the PDF
          # report_file_name = "TEST"
          # pdf_content, _ = report_obj.with_context(**context)._render_qweb_pdf(reportname, docids, data=data)
          #
          # return request.make_response(
          #      pdf_content,
          #      headers=[
          #           ("Content-Type", "application/pdf"),
          #           ("Content-Length", len(pdf_content)),
          #           ("Content-Disposition", f'inline; filename="{report_file_name}.pdf"'),
          #      ],
          # )

     @http.route([
          '/report/<converter>/<reportname>',
          '/report/<converter>/<reportname>/<docids>',
     ], type='http', auth='user', website=True)
     def report_routes(self, reportname, docids=None, converter=None, **data):
          print("\n\n\nreport_routes-------------custom----------------------------")
          if converter == 'html':
               context = dict(request.env.context)
               # Apply additional context from request data
               if data.get("with_company"):
                    context['with_company'] = int(data['with_company'])
               if data.get("cid"):
                    context['allowed_company_ids'] = data['cid']

               if 'allowed_company_ids' in context:
                    # company_id = request.env['res.users'].sudo().browse(int(context['allowed_company_ids'].split(',')[0]))
                    company_id = request.env['res.users'].sudo().browse(int(context['allowed_company_ids'][0]))
               else:
                    company_id = request.env.company

               if data.get("cid"):
                    allowed_company_ids = [int(i) for i in data["cid"].split(",")]
                    context.update(allowed_company_ids=allowed_company_ids)

               request.env = request.env(context=context)

               # Prepare document IDs
               if docids:
                    docids = [int(i) for i in docids.split(",")]
                    report = request.env['ir.actions.report']._get_report_from_name(reportname)
                    records = request.env[report.model].browse(docids)
                    records.check_access_rule('read')
               else:
                    report = request.env['ir.actions.report']._get_report_from_name(reportname)

               # Render html
               report = report.with_company(company_id)
               html = report.with_context(request.env.context)._render_qweb_html(reportname, docids, data=data)[0]
               return request.make_response(html)

          # Prepare context and custom logic for PDF
          if converter == 'pdf':
               context = dict(request.env.context)
               print("data----------------------------------",data)
               # ----------- Handle Options (JSON string) ------------
               if "options" in data:
                    print("if1111111111111")
                    try:
                         print("try---------------------")
                         options_json = urls.url_unquote_plus(data.pop("options"))
                         options = json.loads(options_json)
                         data.update(options)
                         print("data-----1111------------------", data)
                    except Exception as e:
                         print("exception----------------------")
                         return request.make_response(f"Invalid options: {str(e)}", [('Content-Type', 'text/plain')])

               # ----------- Handle Context (JSON string) ------------
               if "context" in data:
                    print("if 22222222222222222")
                    try:
                         print("try---------------------")
                         context_json = urls.url_unquote_plus(data["context"])
                         context.update(json.loads(context_json))
                         print("context-------------------", context)
                    except Exception as e:
                         print("exception----------------------")
                         return request.make_response(f"Invalid context: {str(e)}", [('Content-Type', 'text/plain')])

               if data.get("with_company"):
                    context['with_company'] = int(data['with_company'])
               if data.get("cid"):
                    context['allowed_company_ids'] = data['cid']
               print("context----------------------------",context)
               if 'allowed_company_ids' in context:
                    # allowed_companies = context['allowed_company_ids']
                    # if isinstance(allowed_companies, str):
                    #      company_id = request.env['res.users'].sudo().browse(int(allowed_companies.split(',')[0]))
                    # elif isinstance(allowed_companies, list):
                    #      company_id = request.env['res.users'].sudo().browse(int(allowed_companies[0]))
                    # else:
                    #      company_id = request.env.company
                    company_id = request.env['res.users'].sudo().browse(int(context['allowed_company_ids'][0]))
                    # company_id = request.env['res.users'].sudo().browse(int(context['allowed_company_ids'].split(',')[0]))
                    print("company_id------111-------------------",company_id)
               else:
                    company_id = request.env.company
                    print("company_id------2222-------------------", company_id)

               # Set allowed companies explicitly if provided
               if data.get("cid"):
                    allowed_company_ids = [int(i) for i in data["cid"].split(",")]
                    context.update(allowed_company_ids=allowed_company_ids)

               request.env = request.env(context=context)
               print("context----------222--------------",context)

               # Prepare document IDs
               if docids:
                    docids = [int(i) for i in docids.split(",")]
                    report = request.env['ir.actions.report']._get_report_from_name(reportname)
                    records = request.env[report.model].browse(docids)
                    records.check_access_rule('read')
               else:
                    report = request.env['ir.actions.report']._get_report_from_name(reportname)

               # Render PDF
               report = report.with_company(company_id)
               print("report------------------------------",report)
               print("context---------------3333---------------",context)
               pdf = report.with_context(**context)._render_qweb_pdf(reportname, docids, data=data)[0]
               pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
               return request.make_response(pdf, headers=pdfhttpheaders)

          return super().report_routes(reportname, docids=docids, converter=converter, **data)
