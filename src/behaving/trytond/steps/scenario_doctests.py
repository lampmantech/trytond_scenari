# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""

This is a straight cut-and-paste from
trytond_*-2.8.*/tests/scenario_*.rst
to refactor the doctests to eliminate duplication.
All the steps in this file are used by all of
the feature files that impelment the doctest scenari.

The aim is to make each step idempotent, so that if
you run a step again from another feature file,
the work is not repeated, and will not error.
That's easy in the early steps, but harder farther on,
so some feature files will need to be run on their own.
Most steps are commented as either idempotent or FixMe.

It should be improved to be more like a Behave BDD.
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support.stepfuns import vAssertContentTable
from .support.stepfuns import gGetFeaturesPayRec, \
    vSetNamedInstanceFields, vSetDescribedInstanceFields
from .support import stepfuns
from .support import modules
from .support.tools import *

today = datetime.date.today()

@step('Create database')
def step_impl(context):
    pass

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *
@step('Set the default feature data')
def step_impl(context):
    """
    You can use this step to define a set of default feature data
    that will be available using the vSetFeatureData and vSetFeatureData
    functions to pass data between steps. The default data is pulled
    from the Tryton code, but you can override this for your own
    production Chart of Accounts, users...
    """
    assert type(context.dData['feature']) == dict
    uDefaults = u'''
    Given Set the feature data with values
     | name                                      | value                      |
     | party,company_name                        | {company_name}             |
     | account.account,minimal_account_root      | {minimal_account_root}     |
     | account.template,minimal_account_template | {minimal_account_template} |
     | user,accountant,name                      | {accountant_name}          |
     | user,accountant,login                     | {accountant_login}         |
     | user,accountant,password                  | {accountant_password}      |
     | user,accountant,email                     | {accountant_email}         |
     | account.template,main_receivable          | {main_receivable}          |
     | account.template,main_payable             | {main_payable}             |
     | account.template,main_revenue             | {main_revenue}             |
     | account.template,main_expense             | {main_expense}             |
     | account.template,main_cash                | {main_cash}                |
     | account.template,main_input_tax           | {main_input_tax}           |
     | account.template,main_asset               | {main_asset}               |
     | account.template,main_depreciation        | {main_depreciation}        |
'''
    uDefaults = uDefaults.format(
        company_name=COMPANY_NAME, # "B2CK"
        minimal_account_root=MINIMAL_ACCOUNT_ROOT,
        minimal_account_template=MINIMAL_ACCOUNT_TEMPLATE,
        accountant_name=ACCOUNTANT_NAME, # 'Accountant'
        accountant_login=ACCOUNTANT_USER, # 'accountant'
        accountant_password=ACCOUNTANT_PASSWORD, # 'accountant'
        # our addition
        accountant_email=ACCOUNTANT_EMAIL, # 'accountant@example.com'
        # from trytond_account-3.0.0/account.xml
        main_receivable='Main Receivable',
        main_payable='Main Payable',
        main_revenue='Main Revenue',
        main_expense='Main Expense',
        main_cash='Main Cash',
        main_input_tax='Main Tax',
        main_asset='Assets',
        main_depreciation='Depreciation',
        )
    context.execute_steps(uDefaults)

@step('Set the feature data with values')
def step_impl(context):
    """
    You can use this step to define a set of default feature data
    that will be available using the vSetFeatureData and vSetFeatureData
    functions to pass data between steps. It expects a |name|value| table.
    """
    assert type(context.dData['feature']) == dict
    for row in context.table:
        vSetFeatureData(context, row['name'], row['value'])

@step('Create database with pool.test set to True')
def step_impl(context):
    # FixMe: what does this do?
    """
    Sets pool.test set to True
    """
    # This is cute
    current_config = context.oProteusConfig
    current_config.pool.test = True

# account_stock_anglo_saxon
@step('Install the test module named "{uName}"')
def step_impl(context, uName):
    # FixMe: what does this do?
    """
    Installs a module using trytond.tests.test_tryton.install_module
    in case thats different to installing a module.
    """
    from trytond.tests.test_tryton import install_module
    install_module(uName)

@step('Create the Company with default COMPANY_NAME and Currency code "{uCode}"')
def step_impl(context, uCode):
    """
    Given \
    Create the Company with default COMPANY_NAME and Currency code "{uCode}"
    """
    uPartyName = sGetFeatureData(context, 'party,company_name')
    context.execute_steps(u'''
Given Create the Company associated with the party named "%s" and using the currency "%s"
''' % (uPartyName, uCode,)
                          )

# ['code', 'create_date', 'addresses', 'supplier_location', 'write_uid', 'customer_location', 'full_name', 'vat_number', 'id', 'receivable', 'create_uid', 'receivable_today', 'account_payable', 'code_readonly', 'code_length', 'vat_code', 'email', 'website', 'rec_name', 'fax', 'account_receivable', 'customer_tax_rule', 'payable', 'contact_mechanisms', 'write_date', 'active', 'categories', 'lang', 'supplier_tax_rule', 'name', 'phone', 'mobile', 'supplier_payment_term', 'vat_country', 'customer_payment_term', 'payable_today']

@step('Create the Company associated with the party named "{uParty}" and using the currency "{uCode}"')
def step_impl(context, uParty, uCode):

    Company = proteus.Model.get('company.company')
    Party = proteus.Model.get('party.party')

    if uParty:
        uPartyName = uParty
    else:
        uPartyName = sGetFeatureData(context, 'party,company_name')
    l = Party.find([('name', '=', uPartyName)])
    if not l:
        oParty = Party(name=uPartyName)
        oParty.save()
    else:
        oParty = l[0]

    if not Company.find([('party.id', '=', oParty.id)]):
        oCompanyConfig = proteus.Wizard('company.company.config')
        oCompanyConfig.execute('company')
        oCompanyConfigForm = oCompanyConfig.form

        oCompanyConfigForm.party = oParty

        Currency = proteus.Model.get('currency.currency')
        currencies = Currency.find([('code', '=', uCode)])
        if not currencies:
            if uCode == 'EUR':
                currency = Currency(name='EUR', symbol=u'€', code='EUR',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.',
                                    mon_thousands_sep=',')
            elif uCode == 'GBP':
                currency = Currency(name='GBP', symbol=u'£', code='GBP',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.',
                                    mon_thousands_sep=',')
            elif uCode == 'USD':
                currency = Currency(name='USD', symbol=u'$', code='USD',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.',
                                    mon_thousands_sep=',')
            elif uCode == 'CAD':
                currency = Currency(name='CAD', symbol=u'$', code='CAD',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.',
                                    mon_thousands_sep=',')
            else:
                assert code in ['EUR', 'GBP', 'USD', 'CAD'], \
                       "Unsupported currency code: %s" % (uCode,)
            currency.save()

            CurrencyRate = proteus.Model.get('currency.currency.rate')
            # the beginning of computer time
            CurrencyRate(date=datetime.date(year=1970, month=1, day=1),
                         rate=Decimal('1.0'),
                         currency=currency).save()
        else:
            currency, = currencies
        oCompanyConfigForm.currency = currency
        oCompanyConfig.execute('add')

    assert Company.find([('party.id', '=', oParty.id)])

@step('Create the currency with Currency code "{uCode}"')
def step_impl(context, uCode):
    """
    Given \
    Create the currency with Currency code "{uCode}"

    You'll need to do this before you use any other currencies
    than the company's base currency.
    """

    Currency = proteus.Model.get('currency.currency')
    currencies = Currency.find([('code', '=', uCode)])
    if not currencies:
        if uCode == 'EUR':
            currency = Currency(name='EUR', symbol=u'€', code='EUR',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point=',')
        elif uCode == 'GBP':
            currency = Currency(name='GBP', symbol=u'£', code='GBP',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        elif uCode == 'USD':
            currency = Currency(name='USD', symbol=u'$', code='USD',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        elif uCode == 'CAD':
            currency = Currency(name='CAD', symbol=u'$', code='CAD',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        else:
            assert code in ['EUR', 'GBP', 'USD', 'CAD'], \
                   "Unsupported currency code: %s" % (uCode,)
        currency.save()


    assert Currency.find([('code', '=', uCode)])

@step('Reload the default User preferences into the context')
def step_impl(context):
    # FixMe: what does this do?
    """
    Reload the default User get_preferences.
    """
    config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

# party.party Supplier
@step('Create a saved instance of "{uKlass}" named "{uName}"')
def step_impl(context, uKlass, uName):
    """
    Given \
    Create an instance of a Model, like Model.get('party.party')
    with the name attribute of 'uName'.
    Idempotent.
    """
    oKlass = proteus.Model.get(uKlass)
    if not oKlass.find([('name', '=', uName)]):
        instance = oKlass(name=uName)
        instance.save()

@step('Create an instance of "{uKlass}" keyed "{uKey}" "{uName}" with |name|value| fields')
def step_impl(context, uKlass, uKey, uName):
    pass

@step('Create an instance of "{uKlass}" named "{uName}" with fields')
@step('Create an instance of "{uKlass}" named "{uName}" with |name|value| fields')
def step_impl(context, uKlass, uName):
    """
    Given \
    Create an instance of a Model, like Model.get('party.party')
    with the name attribute of 'uName' and the fields from the table.
    It expects a |name|value| table.
    Idempotent.
    """
    vAssertContentTable(context, 2)

    Klass = proteus.Model.get(uKlass)
    l = Klass.find([('name', '=', uName)])
    if l:
        oInstance = l[0]
    else:
        oInstance = Klass(name=uName)
    #? save it first vSetNamedInstanceFields(context, uName, uKlass, sSlot='name')
    for row in context.table:
        gValue = string_to_python(row['name'], row['value'], Klass)
        setattr(oInstance, row['name'], gValue )
    oInstance.save()
    assert Klass.find([('name', '=', uName)])

@step('Set the slots of the instance named "{uName}" of model "{uKlass}" to the values')
@step('Set the instance named "{uName}" of model "{uKlass}" with fields')
@step('Set the instance named "{uName}" of model "{uKlass}" with |name|value| fields')
def step_impl(context, uName, uKlass):
    """
    Given \
    Guven an instance named "uName" of a Model, like Model.get('party.party')
    set the attributes to the values.   It expects a |name|value| table.
    Idempotent.
    """
    vSetNamedInstanceFields(context, uName, uKlass)

@step('Set the slots of the instance described "{uName}" of model "{uKlass}" to the values')
@step('Set the instance described "{uName}" of model "{uKlass}" with fields')
@step('Set the instance described "{uName}" of model "{uKlass}" with |name|value| fields')
def step_impl(context, uName, uKlass):
    """
    Given \
    Guven an instance described "uName" of a Model, like Model.get('account.invoice')
    set the attributes to the values.   It expects a |name|value| table.
    Idempotent.
    """
    vSetDescribedInstanceFields(context, uName, uKlass)

@step('I find an instance of "{uKlass}" named "{uName}"')
def step_impl(context, uKlass, uName):
    """
    Find an instance of a Model, like Model.get('party.party')
    Idempotent.
    """
    Klass = proteus.Model.get(uKlass)
    l = Klass.find([('name', '=', uName)])
    assert len(l) == 1

@step('Create parties')
def step_impl(context):
    """
    Given \
    Create a party named "Supplier"
    And \
    Create a party named "Customer"
    """
    context.execute_steps(u'''Given Create a party named "Supplier"''')
    context.execute_steps(u'''Given Create a party named "Customer"''')

@step('Create a party named "{uName}"')
def step_impl(context, uName):
#    context.execute_steps(u'''
#    Given Create a saved instance of "party.party" named "%s"
#    ''' % (uName,))
    Party = proteus.Model.get('party.party')
    if not Party.find([('name', '=', uName)]):
        oParty = Party(name=uName)
        oParty.save()


# Customer
@step('Create a party named "{uName}" with Payable and Receivable')
@step('Create a party named "{uName}" with an account_payable attribute')
@step('Create a party named "{uName}" with payable and receivable properties')
def step_impl(context, uName):
    """
    Given \
    Create a party named "uName" with payable and receivable properties.

    The account_payable Account is taken from the
    'account.template,main_payable' entry of the feature data
    (use 'Set the feature data with values' to override)
    Idempotent.
    """
    Party = proteus.Model.get('party.party')
    Company = proteus.Model.get('company.company')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    stepfuns.vCreatePartyWithPayRec(context, uName, company)

@step('Create a party named "{uName}" with payable and receivable properties with fields')
@step('Create a party named "{uName}" with payable and receivable properties with |name|value| fields')
def step_impl(context, uName):
    """
    Given \
    Create a party named "uName" with payable and receivable properties. \

    The account_payable Account is taken from the
    'account.template,main_payable' entry of the feature data
    (use 'Set the feature data with values' to override)
    Then use the following |name|value| fields to set fields on the party.
    Idempotent.
    """
    Party = proteus.Model.get('party.party')
    Company = proteus.Model.get('company.company')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    stepfuns.vCreatePartyWithPayRec(context, uName, company)
    vSetNamedInstanceFields(context, uName, 'party.party')

# Accountant, Account
@step('Create a user named "{uName}" with the fields')
@step('Create a user named "{uName}" with the |name|value| fields')
def step_impl(context, uName):
    """
    Given \
    Create a res.user named 'uName' and the given field values.
    It expects a |name|value| table.
    If one of the field names is 'group', it will add the User to that group.
    It also loads the values into the feature data under the  keys
    'user,'+uName+","+row['name']
    Idempotent.
    """
    User = proteus.Model.get('res.user')

    if not User.find([('name', '=', uName)]):
        Group = proteus.Model.get('res.group')

        user = User()
        user.name = uName
        # login password
        for row in context.table:
            if row['name'] == u'group':
                # multiple allowed?
                group, = Group.find([('name', '=', row['value'])])
                user.groups.append(group)
                continue
            setattr(user, row['name'],
                    string_to_python(row['name'], row['value'], User))
            sKey = 'user,'+uName+","+row['name']
            context.dData['feature'][sKey] = row['value']
        user.save()

        assert User.find([('name', '=', uName)])

@step('Create a grouped user named "{uName}" with |name|value| fields')
def step_impl(context, uName):
    """
    Given \
    Create a user named "{uName}" with |name|value| fields
            | name   | value |
            | login  | sale  |
            | group  | Sales |
    group can be repeated for list of groups.
    """
    Party = proteus.Model.get('party.party')
    Company = proteus.Model.get('company.company')
    uPartyName = sGetFeatureData(context, 'party,company_name')
    oParty, = Party.find([('name', '=', uPartyName)])
    company, = Company.find([('party.id', '=', oParty.id)])

    User = proteus.Model.get('res.user')
    if not User.find([('name', '=', uName)]):
        oUser = User(name=uName)
        oUser.main_company = company
        Group = proteus.Model.get('res.group')
        for row in context.table:
            if row['name'] == 'group':
                oGroup, = Group.find([('name', '=', row['value'])])
                oUser.groups.append(oGroup)
                continue
            setattr(oUser, row['name'],
                    string_to_python(row['name'], row['value'], User))
        oUser.save()
    oUser, = User.find([('name', '=', uName)])
    return oUser


@step('Create a sale user')
def step_impl(context):
    """
    Given \
    Create a grouped user named "Sale" with |name|value| fields
            | name   | value |
            | login  | sale  |
            | group  | Sales |
    """
    User = proteus.Model.get('res.user')
    context.execute_steps(u'''
    Given Create a grouped user named "%s" with |name|value| fields
            | name   | value |
            | login  | sale  |
            | group  | Sales |
    ''' % ('Sale',))

@step('Create a purchase user')
def step_impl(context):
    """
    Given \
    Given Create a grouped user named "Purchase" with |name|value| fields
            | name   | value            |
            | login  | purchase         |
            | group  | Purchase         |
    """
    User = proteus.Model.get('res.user')
    context.execute_steps(u'''
    Given Create a grouped user named "%s" with |name|value| fields
            | name   | value            |
            | login  | purchase         |
            | group  | Purchase         |
    ''' % ('Purchase',))

@step('Create a stock user')
def step_impl(context):
    """
    Given Create a grouped user named "Stock" with |name|value| fields
            | name   | value |
            | login  | stock |
            | group  | Stock |
    """
    User = proteus.Model.get('res.user')
    context.execute_steps(u'''
    Given Create a grouped user named "%s" with |name|value| fields
            | name   | value |
            | login  | stock |
            | group  | Stock |
    ''' % ('Stock',))
    stock_user, = User.find([('name', '=', 'Stock')])


@step('Create a account user')
@step('Create an account user')
def step_impl(context):
    """
    Given \
    Create a grouped user named "Account" with |name|value| fields
            | name   | value |
            | login  | account |
            | group  | Account |
    """
    User = proteus.Model.get('res.user')
    context.execute_steps(u'''
    Given Create a grouped user named "%s" with |name|value| fields
            | name   | value |
            | login  | account |
            | group  | Account |
    ''' % ('Account',))


@step('Create a product user')
def step_impl(context):
    """
    Given \
    Create a grouped user named "Product" with |name|value| fields
            | name   | value                  |
            | login  | product                |
            | group  | Product Administration |
    """

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    product_admin_user = User()
    product_admin_user.name = 'Product'
    product_admin_user.login = 'product'
    product_admin_user.main_company = company
    product_admin_group, = Group.find([
        ('name', '=', 'Product Administration')
    ])
    product_admin_user.groups.append(product_admin_group)
    product_admin_user.save()

    product_admin_user, = User.find([('name', '=', 'Product')])

@step('Create a stock_admin user')
def step_impl(context):
    """
    Given \
    Create a grouped user named "Stock Admin" with |name|value| fields
            | name   | value                |
            | login  | stock_admin          |
            | group  | Stock Administration |
    """

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    stock_admin_user = User()
    stock_admin_user.name = 'Stock Admin'
    stock_admin_user.login = 'stock_admin'
    stock_admin_user.main_company = company
    stock_admin_group, = Group.find([('name', '=', 'Stock Administration')])
    stock_admin_user.groups.append(stock_admin_group)
    stock_admin_user.save()

    assert User.find([('name', '=', 'Stock Admin')])

