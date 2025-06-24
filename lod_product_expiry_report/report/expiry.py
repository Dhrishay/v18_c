from odoo import api,models,fields
from datetime import datetime,timedelta


class ExpiryReportTemplate(models.AbstractModel):
    _name = 'report.lod_product_expiry_report.product_exp_report'
    _description= '0 report'
     
    def domain(self,**kwargs):
        if kwargs['group_by']=='location': 
            end_provious_date = fields.datetime.today() + timedelta(days=kwargs['num_expiry_days']) 
            domain = [
                    ('lot_id.expiration_date', '>=', datetime.today()), 
                    ('lot_id.expiration_date', '<=', end_provious_date), 
                    ('location_id', 'in', kwargs['location_ids']),  
                    ] 
            return domain 
        if kwargs['group_by']=='product': 
            end_provious_date = fields.datetime.today() + timedelta(days=kwargs['num_expiry_days']) 
            domain = [
                    ('lot_id.expiration_date', '>=', datetime.today()), 
                    ('lot_id.expiration_date', '<=', end_provious_date), 
                    ('product_id', 'in', kwargs['product_ids']),  
                    ] 
            return domain 
        else: 
            end_provious_date =fields.datetime.today() + timedelta(days=kwargs['num_expiry_days'])
            domain = [
                    ('lot_id.expiration_date', '>=', datetime.today()),     
                    ('lot_id.expiration_date', '<=', end_provious_date),     
                    ('product_id.categ_id', 'in', kwargs['category_ids']),  
                    ] 
            return domain 
    
    @api.model
    def _get_report_values(self, docids,data=None): 
        data_form= data.get('data')
        docs = self.env['report.download.wizard'].browse(data_form['id']) 
        
        domain = self.domain(**data_form) 
        today=datetime.today()
        
        expiry_move = self.env['stock.quant'].search(domain) 
          
        return {   
            'docs': docs,  
            'today':today,
            'expiry_move':expiry_move,  
        }