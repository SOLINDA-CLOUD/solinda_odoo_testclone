# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class MerkRecoment(models.Model):
#     _name = 'meek.recoment'
#     _description = 'Merk Recommended'

#     name = fields.Char(string='Merk Recommended')
#     purchase_ids = fields.Many2one('purchase.order.line', string='Purchase')

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    merk_try = fields.Char('Merk')

class DeliveryLocation(models.Model):
    _name = 'delivery.location'
    _description = 'Delivery Location'

    name = fields.Char(string='Delivery Location')
    # delivery_location_ids = fields.Many2one('purchase.requisition.line', string='purchase', inverse_name='delivery_location_id')

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    merk_recommended = fields.Many2one('res.partner', string='Merk Recommended')
    price_target = fields.Float('Price Target')
    date_plan_required = fields.Date('Date Plan Required')
    delivery_location_id = fields.Many2one(string='Delivery Location', comodel_name='delivery.location', ondelete='restrict')
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_uom = fields.Many2one('uom.uom')
    disc_po = fields.Float(string='Disc.%')
    price_subtotal = fields.Monetary(compute='_compute_price_subtotal', store=True)

    @api.depends('price_unit','disc_po')
    def _compute_price_subtotal(self):
        for this in self:
            this.price_subtotal = this.price_unit * (this.disc_po / 100)

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     project_code_id = fields.Many2one('project.code.pr', string='Project Code')

# class PurchaseRequest(models.Model):
#     _inherit = 'purchase.request'

# class PurchaseRequest(models.Model):
#     _inherit = 'purchase.request'

#     project_code = fields.Char(string='Project Code')
#     budget_code = fields.Char(string='Budget Code')
