from odoo import api, fields, models, _
from datetime import datetime, time
import pytz


class DOLWizard(models.TransientModel):
    _name = "load.product.newtagprice.wizard"
    _description = "Load Product New Tag Price Wizard"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user.id,
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company.id,
        string="Company",
    )
    location_id = fields.Many2one(related="company_id.location_id", string="Location")

    @api.onchange("company_id")
    def _onchange_company_id(self):
        for res in self:
            res.location_id = res.company_id.location_id.id
        return {}

    description = fields.Char(string="Description")
    date_update = fields.Date(string="Date")

    def confirm_load_data(self):
        branch = self.env.context.get("branch_type")
        batch_update_price_id = None
        if self.date_update:
            source_timezone = pytz.timezone(self.env.context.get("tz"))
            start_date = datetime.combine(self.date_update, time(0, 0, 0))
            end_date = datetime.combine(self.date_update, time(23, 59, 59))
            start_localized_time = source_timezone.localize(start_date)
            end_localized_time = source_timezone.localize(end_date)

            # Convert the localized time to UTC
            start_utc_time = start_localized_time.astimezone(pytz.utc)
            end_utc_time = end_localized_time.astimezone(pytz.utc)
            batch_update_price_id = self.env["batch.update.price"].search(
                [
                    ("status", "=", "updated"),
                    ("dat_update", ">=", start_utc_time),
                    ("dat_update", "<=", end_utc_time),
                ]
            )
        else:
            batch_update_price_id = self.env["batch.update.price"].search(
                [("status", "=", "updated")], order="id desc", limit=1
            )

        product_ids = (
            batch_update_price_id.batch_line_ids.product_id.product_variant_id.ids
        )

        order_point_id = self.env["stock.warehouse.orderpoint"].search(
            [
                ("location_id", "=", self.location_id.id),
                ("product_id", "in", product_ids),
            ]
        )
        # 1 is ID branch Phonsinuan
        if branch == "kkm" and self.company_id.id == 1:
            product_list = batch_update_price_id.batch_line_ids.product_id.ids
        #comment this code because currently not used branch == "fc" when added menu in opration this changes will be update
        # elif branch == "kkm" and self.company_id.id != 1 or branch == "fc":
        elif branch == "kkm" and self.company_id.id != 1:
            product_list = order_point_id.product_tmpl_id.ids
        else:
            product_ids = []
        return {
            "name": _("Product Template"),
            "view_mode": "list",
            "view_id": self.env.ref(
                "lo_inventory_enhancemnet.product_template_updated_new_price_view_list"
            ).id,
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", product_list)],
            "target": "current",
            "context": dict(self._context, create=False),
        }
