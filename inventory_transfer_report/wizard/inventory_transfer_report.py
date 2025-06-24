from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
import xlsxwriter
from odoo import models
from odoo.http import content_disposition
from odoo.tools.misc import xlsxwriter
import io
from datetime import datetime, time
from pytz import timezone, UTC


class InventoryTransferReport(models.TransientModel):
    _name = "report.inventory.transfer"
    _description = "inventory transfer report"

    start_date = fields.Date("Start date", required=True)
    end_date = fields.Date("End date", required=True)
    report_name = fields.Selection(
        [("transfer_in", "Transfer In"), ("transfer_out", "Transfer Out")],
        default="transfer_out",
        required=True,
    )
    location_id = fields.Many2one("stock.location", "Source Location")
    location_dest_id = fields.Many2one("stock.location", string="Destination Location")

    def get_company_domain(self):
        return [("id", "in", self.env.companies.ids)]

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        default=lambda self: self.env.company.id,
        domain=get_company_domain,
    )

    print_out = fields.Selection(
        [("pdf", "PDF"), ("xlsx", "XLSX")], string="Output Format", required=True
    )

    def _get_sql_query(self):
        query = "SELECT sp.id FROM stock_picking sp WHERE "
        conditions = []

        user_tz_str = self.env.user.tz or "UTC"
        user_tz = timezone(user_tz_str)

        # Convert date to datetime before localizing
        start_datetime = datetime.combine(self.start_date, time.min)
        end_datetime = datetime.combine(self.end_date, time.max)
        # converted the dates to fetch correct records!
        from_date_utc = user_tz.localize(start_datetime).astimezone(UTC)
        to_date_utc = user_tz.localize(end_datetime).astimezone(UTC)

        #Action Domains for In and Out
        if self.report_name == "transfer_in":
            conditions.append("sp.request_type = TRUE")
            conditions.append(
                "sp.picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'incoming')"
            )
            conditions.append(
                "EXISTS ("
                "SELECT 1 FROM stock_move sm "
                "WHERE sm.picking_id = sp.id AND sm.purchase_line_id IS NOT NULL"
                ")"
            )

        # if self.report_name == "transfer_in":
        #     conditions.append("sp.request_type = TRUE")
        #     conditions.append(
        #         "sp.picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'incoming')"
        #     )
        #     conditions.append(
        #         "("
        #         "sp.sale_id IS NOT NULL OR "
        #         "EXISTS ("
        #         "SELECT 1 FROM stock_move sm "
        #         "JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id "
        #         "WHERE sm.picking_id = sp.id"
        #         ")"
        #         ")"
        #     )

        elif self.report_name == "transfer_out":
            conditions.append("sp.request_type = TRUE")
            conditions.append(
                "("
                "sp.sale_id IS NOT NULL OR "
                "sp.picking_type_id IN (SELECT id FROM stock_picking_type WHERE code = 'outgoing')"
                ")"
            )
            # conditions.append("sp.state = 'done'")

        # Dynamic filters
        if from_date_utc:
            conditions.append(f"sp.scheduled_date >= '{from_date_utc}'")
        if to_date_utc:
            conditions.append(f"sp.scheduled_date <= '{to_date_utc}'")
        if self.location_id:
            conditions.append(f"sp.location_id = {self.location_id.id}")
        if self.location_dest_id:
            conditions.append(f"sp.location_dest_id = {self.location_dest_id.id}")
        if self.company_id:
            conditions.append(f"sp.company_id = {self.company_id.id}")

        # Combine conditions
        if conditions:
            query += " AND ".join(conditions)
        else:
            query += "1=1"

        query += " ORDER BY sp.id"
        return query

    def print_pdf_xlsx(self):
        # Get the SQL query string
        query = self._get_sql_query()

        # Execute the query in the database
        self.env.cr.execute(query)

        # Fetch the results (ids of stock.picking)
        pickings_ids = [picking[0] for picking in self.env.cr.fetchall()]

        # Filter out pickings based on the fetched ids
        # pickings = self.env["stock.picking"].search([('id','in',pickings_ids)])
        pickings = self.env["stock.picking"].browse(pickings_ids)

        user_tz_str = self.env.user.tz or "UTC"
        user_tz = timezone(user_tz_str)
        formatted_dates = {
            picking.name: (
                picking.scheduled_date.astimezone(user_tz).strftime("%d/%m/%Y")
                if picking.scheduled_date
                else ""
            )
            for picking in pickings
        }

        data = {
            "data": {
                "start_date": str(self.start_date),
                "end_date": str(self.end_date),
                "report_name": self.report_name,
                "company_name": self.company_id.name,
                "pickings": pickings.ids,
                "company_zone_id": self.company_id.zone_id.name,
                "company_district_id": self.company_id.district_id.name,
            },
            "formatted_dates": formatted_dates,
        }
        print("asdhfashgdfashdgfashg", data["data"]["pickings"])
        if self.print_out == "pdf":
            # Generate Pdf
            return self.env.ref(
                "inventory_transfer_report.action_transfer_pdf_report"
            ).report_action(
                self,
                data=data,
            )
        else:
            # Generate Excel
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {"in_memory": True})
            worksheet = workbook.add_worksheet("Inventory Transfer")

            # Formats
            title_format = workbook.add_format(
                {"bold": True, "font_size": 14, "align": "center"}
            )
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#D9D9D9",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "font_color": "black",
                }
            )
            cell_format = workbook.add_format({"border": 1, "align": "center"})
            currency_format = workbook.add_format(
                {"border": 1, "num_format": "#,##0.00", "align": "right"}
            )
            qty_format = workbook.add_format({"border": 1, "align": "right"})

            # Report title & metadata
            worksheet.merge_range("A1:G1", "Inventory Transfer Report", title_format)
            worksheet.merge_range(
                "A2:G2",
                f"Report: {'Transfer In' if self.report_name == 'transfer_in' else 'Transfer Out'}",
                cell_format,
            )
            worksheet.merge_range(
                "A3:G3", f"Store: {self.company_id.name}", cell_format
            )
            worksheet.merge_range(
                "A4:G4",
                f"Address: {self.company_id.zone_id.name}, {self.company_id.district_id.name}",
                cell_format,
            )
            worksheet.merge_range(
                "A5:G5",
                f"Date: {self.start_date.strftime('%d/%m/%Y') if self.start_date else 'N/A'} to {self.end_date.strftime('%d/%m/%Y') if self.end_date else 'N/A'}",
                cell_format,
            )

            # Headers
            headers = [
                "NO",
                "RCV DATE" if self.report_name == "transfer_in" else "TRANSFER DATE",
                "TRANSFER DATE" if self.report_name == "transfer_in" else "RCV DATE",
                (
                    "ORIGINAL STORE"
                    if self.report_name == "transfer_in"
                    else "DESTINATION STORE"
                ),
                "TRANSFER NO.",
                "QTY",
                "COST AMOUNT",
            ]
            worksheet.write_row("A7", headers, header_format)

            # Data rows
            total_qty = 0
            total_cost = 0
            row = 7
            count = 1

            for picking in pickings:
                for move in picking.move_ids_without_package:
                    qty = move.product_uom_qty
                    cost = qty * move.product_id.standard_price
                    total_qty += qty
                    total_cost += cost
                    user_tz_str = self.env.user.tz or "UTC"
                    user_tz = timezone(user_tz_str)
                    formatted_dates = {
                        picking.name: (
                            picking.scheduled_date.astimezone(user_tz).strftime(
                                "%d/%m/%Y"
                            )
                            if picking.scheduled_date
                            else ""
                        )
                        for picking in pickings
                    }

                    if self.report_name == "transfer_in":
                        values = [
                            count,
                            (
                                formatted_dates[picking.name]
                                if formatted_dates[picking.name]
                                else ""
                            ),
                            (
                                formatted_dates[picking.name]
                                if formatted_dates[picking.name]
                                else ""
                            ),
                            picking.location_id.display_name or "",
                            picking.name,
                            qty,
                            cost,
                        ]
                    else:
                        values = [
                            count,
                            (
                                picking.scheduled_date.strftime("%d/%m/%Y")
                                if picking.scheduled_date
                                else ""
                            ),
                            (
                                picking.date_done.strftime("%d/%m/%Y")
                                if picking.date_done
                                else ""
                            ),
                            picking.location_dest_id.name or "",
                            picking.name,
                            qty,
                            cost,
                        ]

                    worksheet.write(row, 0, values[0], cell_format)
                    worksheet.write(row, 1, values[1], cell_format)
                    worksheet.write(row, 2, values[2], cell_format)
                    worksheet.write(row, 3, values[3], cell_format)
                    worksheet.write(row, 4, values[4], cell_format)
                    worksheet.write_number(row, 5, values[5], qty_format)
                    worksheet.write_number(row, 6, values[6], currency_format)

                    row += 1
                    count += 1

            # Totals row
            worksheet.merge_range(row, 0, row, 4, "Total by Store", header_format)
            worksheet.write_number(row, 5, total_qty, header_format)
            worksheet.write_number(row, 6, total_cost, currency_format)

            # Adjust column widths
            worksheet.set_column("A:A", 6)
            worksheet.set_column("B:C", 15)
            worksheet.set_column("D:D", 25)
            worksheet.set_column("E:E", 20)
            worksheet.set_column("F:G", 14)

            # Finalize
            workbook.close()
            output.seek(0)

            file_data = base64.b64encode(output.getvalue())
            filename = f"Inventory_Transfer_{'In' if self.report_name == 'transfer_in' else 'Out'}_{fields.Date.today()}.xlsx"

            attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "type": "binary",
                    "datas": file_data,
                    "res_model": self._name,
                    "res_id": self.id,
                    "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                }
            )

            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content/{attachment.id}?download=true",
                "target": "self",
            }
