# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

#? shipment_method
@step('Sale on date "{uDate}" with description "{uDescription}" as user named "{uUser}" products to customer "{uCustomer}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |product|quantity|description| fields')
def step_impl(context, uDate, uDescription, uUser, uCustomer, uTerm, uMethod):
    """
    Sale on date "TODAY" with description "Description"
    as user named "Sale" products to customer "Customer" 
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |product|quantity|description| fields
      | product | quantity | description |
      | product | 2.0      |             |
      | product | comment  | Comment     |
      | product | 3.0      |             |
    """
    # shouls we make quantity == 'comment'
    config = context.oProteusConfig

    Sale = proteus.Model.get('sale.sale')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    Product = proteus.Model.get('product.product')
    customer, = Party.find([('name', '=', uCustomer),])

    User = proteus.Model.get('res.user')
    sale_user, = User.find([('name', '=', uUser)])
    proteus.config.user = sale_user.id

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', uTerm)])

    if not Sale.find([('description', '=', uDescription),
                      ('company.id',  '=', company.id),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        # also has shipment_method: 'manual', 'Manual', 'order', 'invoice',

        sale.party = customer
        sale.payment_term = payment_term
        sale.invoice_method = uMethod
        sale.description = uDescription
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        sale.sale_date = oDate
        # sales also have warehouse, currency
        sale.save()

        SaleLine = proteus.Model.get('sale.line')
        for row in context.table:
            product, = Product.find([('name', '=', row['product'])])
            sale_line = SaleLine()
            sale.lines.append(sale_line)
            sale_line.product = product
            if row['quantity'] == 'comment':
                sale_line.type = 'comment'
            else:
                # type == 'line'
                sale_line.quantity = float(row['quantity'])
            if row['description']:
                sale_line.description = row['description'] or ''
            #? why no sale_line.save()
        sale.save()
        
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id
    
    sale, = Sale.find([('description', '=', uDescription),
                       ('company.id',  '=', company.id),
                       ('party.id', '=', customer.id)])


@step('Sale "{uAct}" on date "{uDate}" the S. O. with description "{uDescription}" as user named "{uUser}" products from customer "{uCustomer}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uCustomer):
    """
    Sale "quote" on date "TODAY" the S.O. with description "P. O #1" 
    as user named "Sale" products from customer "Customer"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    customer, = Party.find([('name', '=', uCustomer),])
    Sale = proteus.Model.get('sale.sale')
    sale, = Sale.find([('party.id',  '=', customer.id),
                       ('company.id',  '=', company.id),
                       ('description', '=', uDescription)])

    sale_user, = User.find([('name', '=', uUser)])
    proteus.config.user = sale_user.id
    if uAct == 'quote':
        Sale.quote([sale.id], config.context)
        assert sale.state == u'quotation'
    elif uAct == 'confirm':
        Sale.confirm([sale.id], config.context)
        assert sale.state == u'confirmed'
    elif uAct == 'process':
        Sale.process([sale.id], config.context)
        assert sale.state == u'processing'
    else:
        raise ValueError("uAct must be one of quote confirm process: " + uAct)
    sale.reload()
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

#See also @step('T/ASAS/SASAS Send 5 products on the S. O. with description "{uDescription}" to customer "{uCustomer}"')

@step('Invoice "{uAct}" on date "{uDate}" the S. O. with description "{uDescription}" as user named "{uUser}" products from customer "{uCustomer}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uCustomer):
    """
    Invoice "post" on date "TODAY" the S. O. with description "S. O #1" 
    as user named "Account" products from customer "Customer"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    customer, = Party.find([('name', '=', uCustomer),])
    Sale = proteus.Model.get('sale.sale')
    sale, = Sale.find([('party.id',  '=', customer.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])
    
    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    Invoice = proteus.Model.get('account.invoice')
    invoice = Invoice(sale.invoices[0].id)
    if uDate.lower() == 'today' or uDate.lower() == 'now':
        oDate = TODAY
    else:
        oDate = datetime.date(*map(int, uDate.split('-')))
    invoice.invoice_date = oDate
    if uAct == u'post':
        invoice.click('post')
    else:
        raise ValueError("uAct must be one of quote or confirm: " + uAct)
    invoice.reload()
    
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id


@step('Validate shipments for S. O. with description "{uDescription}" as user named "{uUser}" for products to customer "{uCustomer}"')
def step_impl(context, uDescription, uUser, uCustomer):
    """
    Thia ia a cut-and-paste from the Purchase Validate shipments
    will purchase -> sale etc.
    Not sure if its right it assumes the shipment already has been made

    """
    config = context.oProteusConfig
    
    ShipmentOut = proteus.Model.get('stock.shipment.out')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    customer, = Party.find([('name', '=', uCustomer),])
    Sale = proteus.Model.get('sale.sale')
    sale, = Sale.find([('party.id',  '=', customer.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])

    User = proteus.Model.get('res.user')
    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    
    Move = proteus.Model.get('stock.move')
    shipment = ShipmentOut()
    shipment.customer = customer
    for move in sale.moves:
        outgoing_move = Move(id=move.id)
        shipment.outgoing_moves.append(outgoing_move)
    shipment.save()
    
    assert shipment.origins == sale.rec_name
    ShipmentOut.wait([shipment.id], config.context)
    assert shipment.state == u'waiting'

    assert shipment.origins == sale.rec_name
    ShipmentOut.assign_try([shipment.id], config.context)
    assert shipment.state == u'assigned'

    shipment.reload()
    ShipmentOut.pack([shipment.id], config.context)
    assert shipment.state == u'packed'

    shipment.reload()
    ShipmentOut.done([shipment.id], config.context)
    assert shipment.state == u'done'
    sale.reload()
    
    assert len(sale.shipments) >= 1

    
