from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    tried = fields.Char('Merk')

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    project_code = fields.Char('Project Code')
    budget_code = fields.Char('Budget Code')