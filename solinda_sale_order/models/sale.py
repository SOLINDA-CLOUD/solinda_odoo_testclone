from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'
    
    payment_schedule_line_ids = fields.One2many('payment.schedule', 'order_id', string='Payment Schedule Line')
    quotation_validity = fields.Char(string = 'Quotation Validity')
    delivery_time = fields.Char(string = 'Delivery Time')
    delivery_point = fields.Char(string = 'Delivery Point')
    price_tnc = fields.Html(string = 'Price')
    payment_terms = fields.Html(string = 'Payment Terms')
    revitalization_period = fields.Char(string = 'Revitalization Period')
    deduct_dp = fields.Boolean('Deduct DP')
    
    @api.onchange('payment_schedule_line_ids')
    def _onchange_payment_schedule_line_ids(self):
        total = sum(self.payment_schedule_line_ids.mapped('total_amount'))
        if total > self.amount_total:
            raise ValidationError("Total in Payment Schedule is greater then total amount in sales")
    
    
class PaymentSchedule(models.Model):
    _name = 'payment.schedule'
    _description = 'Payment Schedule'
    
    order_id = fields.Many2one('sale.order', string='Sale Order')    
    payment_date = fields.Date('Payment Date')
    payment_type = fields.Selection([
        ('dp', 'Down Payment'),
        ('termin', 'Termin'),
        ('retensi', 'Retensi'),
    ], string='Payment Type')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field='currency_id')
    # product_id = fields.Many2one('product.product', string='Service')
    account_id = fields.Many2one('account.account', string='Account')
    name = fields.Char('Description')
    progress = fields.Float('Progress')
    bill = fields.Float('Bill')
    
    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount')
    move_id = fields.Many2one('account.move',string="Invoice")
    move_line_id = fields.Many2many('account.move.line')
    
    
    @api.depends('order_id.amount_total','bill')
    def _compute_total_amount(self):
        for this in self:
            this.total_amount = this.bill * this.order_id.amount_total
    
    def create_invoice(self):
        invoice_vals = self.order_id._prepare_invoice()
        if self.move_id:
            return {
                        'name': '%s - %s'%(self.order_id.name,self.name),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'res_id': self.move_id.id,
            
            }
        else:
            if self.order_id.deduct_dp:
                if self.payment_type == 'termin':                
                    seq = 10
                    data_payment = []
                    for payment in self.order_id.payment_schedule_line_ids:
                        if payment.id != self.id:
                            if payment.move_id:
                                data_payment.append((0,0,{
                                'sequence': seq + 10,
                                'name': payment.name,
                                'account_id': payment.account_id.id,
                                'quantity': 1,
                                'price_unit': -payment.total_amount,
                                'analytic_account_id': self.order_id.analytic_account_id.id,
                                'payment_schedule_ids': [(4, payment.id)]
                            }))
                            else:
                                raise ValidationError("Cannot Processed because a payment schedule %s hasn't made an invoice yet"%payment.name)
                        else:
                            data_payment.append((0,0,{
                            'sequence': 10,
                            'name': self.name,
                            'account_id': self.account_id.id,
                            'quantity': 1,
                            'price_unit': self.total_amount,
                            'analytic_account_id': self.order_id.analytic_account_id.id,
                            'payment_schedule_ids': [(4, self.id)]
                            }))
                            break                
                    invoice_vals['invoice_line_ids'] = data_payment
                    moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    
                else:
                    invoice_vals['invoice_line_ids'] = [(0,0,{
                        'sequence': 10,
                        'name': self.name,
                        'account_id': self.account_id.id,
                        'quantity': 1,
                        'price_unit': self.total_amount,
                        'analytic_account_id': self.order_id.analytic_account_id.id,
                        'payment_schedule_ids': [(4, self.id)]
                    })]
                    moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)    

            else:

                invoice_vals['invoice_line_ids'] = [(0,0,{
                    'sequence': 10,
                    'name': self.name,
                    'account_id': self.account_id.id,
                    'quantity': 1,
                    'price_unit': self.total_amount,
                    'analytic_account_id': self.order_id.analytic_account_id.id,
                    'payment_schedule_ids': [(4, self.id)]
                    
                })]
                moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)
                
            self.write({'move_id': moves.id})
            return {
                            'name': '%s - %s'%(self.order_id.name,self.name),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'account.move',
                            'res_id': moves.id,
                
            }
             
    @api.constrains('amount')
    def _constrains_amount(self):
        for this in self:
            total = this.order_id.amount_total
            if this.amount > total:
                raise ValidationError('Amount field is greater then sales total amount')
    
    # @api.onchange('payment_term_id')
    # def _onchange_payment_term_id(self):
    #     if self.payment_term_id:
    #         days = self.payment_term_id.line_ids[0].days
    #         self.payment_date = self.order_id.date_order + relativedelta(days=days)
    #     else:
    #         self.payment_date = False