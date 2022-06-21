from odoo import _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        res.order_line.write({'po_confirm_date': fields.Date.context_today()})
        return res        

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    
    item_id = fields.Many2one('item.item')
    po_confirm_date = fields.Date('Po Confirm Date')    