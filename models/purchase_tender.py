# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BidType(models.Model):
    _name = 'bid.type'
    _description = 'Bid Type'

    name = fields.Char()


class PurchaseTender(models.Model):
    _name = 'purchase.tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Tender'

    name = fields.Char(required=True)
    organization = fields.Many2one('res.partner')
    tender_no = fields.Char()
    tender_name = fields.Char()
    issue_date = fields.Date()
    closing_date = fields.Date()
    initial_meeting_date = fields.Date()
    bid_type = fields.Many2one('bid.type', string='Bidding Type')
    current_co = fields.Many2one('res.partner')
    price = fields.Float()
    guarantee = fields.Float()
    period = fields.Integer()
    manpower = fields.Integer()
    winner = fields.Many2one('res.partner', compute='compute_winner', store=True)
    winner_price = fields.Float(compute='compute_winner', store=True)
    winner_rate_price = fields.Float(compute='compute_winner', store=True)
    care_rank = fields.Integer()
    to_win = fields.Float(compute='compute_to_win', store=True)
    state = fields.Selection(selection=[
        ('participated', 'Participated'),
        ('interested', 'Interested'),
        ('excepted', 'Excepted'),
        ('postponed', 'Postponed'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ])
    image = fields.Binary(related='organization.image_1920', store=True)

    price_analysis_ids = fields.One2many('purchase.tender.price.analysis', 'tender_id')
    manpower_analysis_ids = fields.One2many('purchase.tender.manpower.analysis', 'tender_id')
    vehicle_analysis_ids = fields.One2many('purchase.tender.vehicle.analysis', 'tender_id')
    material_info_ids = fields.One2many('purchase.tender.material.info', 'tender_id')
    equipment_analysis_ids = fields.One2many('purchase.tender.equipment.analysis', 'tender_id')
    initial_meeting_ids = fields.One2many('purchase.tender.initial.meeting', 'tender_id')

    @api.depends('price', 'winner_price')
    def compute_to_win(self):
        for rec in self:
            if rec.price and rec.winner_price:
                rec.to_win = rec.price - rec.winner_price
            else:
                rec.to_win = 0

    @api.depends('price_analysis_ids')
    def compute_winner(self):
        for rec in self:
            rec.winner = False
            rec.winner_price = False
            rec.winner_rate_price = False
            if rec.price_analysis_ids:
                winner = min([rec.price for rec in rec.price_analysis_ids])
                print('winner>>', winner)
                winners = rec.price_analysis_ids.filtered(lambda p: p.price == winner)
                print('winners>>', winners)
                rec.winner = winners[0].contact.id if winners else False
                rec.winner_price = winners[0].price if winners else False
                rec.winner_rate_price = winners[0].rate if winners else False

    def name_get(self):
        result = []
        for tender in self:
            name = tender.name + (' - ' + tender.tender_no if tender.tender_no else '') + (' - ' + tender.organization.name if tender.organization else '')
            result.append((tender.id, name))
        return result


class TenderPriceAnalysis(models.Model):
    _name = 'purchase.tender.price.analysis'
    _description = 'Purchase Tender Price Analysis'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    rank = fields.Integer()
    contact = fields.Many2one('res.partner')
    price = fields.Float()
    rate = fields.Float(compute='compute_rate', store=True)
    tender_id = fields.Many2one('purchase.tender')

    @api.depends('tender_id.manpower', 'price')
    def compute_rate(self):
        for rec in self:
            if rec.tender_id.manpower and rec.price:
                rec.rate = rec.price / rec.tender_id.manpower
            else:
                rec.rate = 0


class TenderManpowerAnalysis(models.Model):
    _name = 'purchase.tender.manpower.analysis'
    _description = 'Purchase Tender Manpower Analysis'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    qty = fields.Float()
    tender_id = fields.Many2one('purchase.tender')


class TenderVehicleAnalysis(models.Model):
    _name = 'purchase.tender.vehicle.analysis'
    _description = 'Purchase Tender Vehicle Analysis'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    qty = fields.Float()
    tender_id = fields.Many2one('purchase.tender')


class TenderMaterialInfo(models.Model):
    _name = 'purchase.tender.material.info'
    _description = 'Purchase Tender Material Info'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    action = fields.Char()
    tender_id = fields.Many2one('purchase.tender')


class TenderEquipmentAnalysis(models.Model):
    _name = 'purchase.tender.equipment.analysis'
    _description = 'Purchase Tender Equipment Analysis'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    qty = fields.Float()
    tender_id = fields.Many2one('purchase.tender')


class TenderInitialMeeting(models.Model):
    _name = 'purchase.tender.initial.meeting'
    _description = 'Purchase Tender Initial Meeting'

    name = fields.Char(required=True, string="Description")
    sequence = fields.Integer(default=10)
    date = fields.Date()
    file = fields.Binary()
    tender_id = fields.Many2one('purchase.tender')
