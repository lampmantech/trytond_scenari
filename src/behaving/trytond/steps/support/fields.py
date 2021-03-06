# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
Convenience functions.
"""

import datetime
import time
from decimal import Decimal
import proteus

def sGetFeatureData(context, sKey, sDefault=''):
    if sKey in context.dData['feature']:
        return context.dData['feature'][sKey]

    # fall through to oEnvironmentCfg
    lKeys = sKey.split(',', 1)
    assert len(lKeys) == 2
    g = context.oEnvironmentCfg.get(*lKeys)
    if g: return g

    if sDefault: return sDefault
    raise UserError("ERROR: Use 'Set the feature data with values' to set the value of "+sKey)

def vSetFeatureData(context, sKey, sValue):
    context.dData['feature'][sKey] = sValue

def string_to_python (sField, uValue, Party=None):
    #? should replace this with DSL
    

    if Party is None:
        sType = ''
    else:
        dFields = Party._fields
        assert sField in dFields.keys(), \
               "ERROR: Unknown field %s; not in %r" % (sField, dFields.keys(),)
        dField = dFields[sField]
        assert 'type' in dField.keys(), \
               "PANIC: key %s; not in %r" % ('type', dFields.keys(),)
        sType = dField['type']

    if sType == 'boolean':
        if uValue.lower() in ('false', 'nil'): return False
        if uValue.lower() in ('true'): return True
    if sType == 'numeric' or sField.endswith('_price'):
        return Decimal(uValue)
    if sType in ['char', 'text', 'sha']:
        return uValue
    if sType == 'integer':
        return int(uValue)
    if sType == 'float':
        return float(uValue)
    if sType == 'selection':
        # FixMe: are selections always strings or can they be otherwise?
        # sSelection = dField['selection']
        return uValue
    if sType == 'date' or sField.endswith('_date'):
        # FixMe: whats a date format look like on input? Assuming YYYY-MM-DD
        if uValue == 'TODAY': return datetime.date.today()
        return datetime.date(*map(int,uValue.split('-')))

    if sType == 'datetime':
        # FixMe: whats a time format look like on input? Assuming YYYY-MM-DD
        if uValue == 'TODAY': return datetime.datetime.now()
        return datetime.datetime(*map(int,uValue.split('-')))

    if sField in ['name',]:
        return uValue

    # give up or error?
    if sType == '': return uValue

    #? This is not always true
    #assert 'searchable' in dField.keys(), \
    #       "Sorry, dont know how to look in slots of %s " % (sField,)
    #assert dField['searchable']

    # sType == 'many2one' or sType == 'many2many' uses relation
    assert 'relation' in dField.keys(), \
               "PANIC: key %s; not in %r" % ('relation', dFields.keys(),)
    sRelation = dField['relation']

    oClass = proteus.Model.get(sRelation)
    lKeys = dir(oClass)
    #? FixMe: rec_name?
    for sKey in ['name', 'code']:
        if sKey not in lKeys: continue
        lElts = oClass.find([(sKey, '=', uValue)])
        if lElts: break
            
    if len(lElts) == 0 and sField in ['country', 'subdivision']:
        # Were having trouble with country.country as of 3.2
        # This code from trytond_party_vcarddav-3.2.0/party.py doesnt work
        # Country.find([]) returns nothing
        Country = proteus.Model.get('country.country')
        if sField in ['country']:
            countries = Country.find([
                    ('rec_name', '=', uValue),
                    ])
            # , limit=1
            if countries:
                #? .rec_name
                return countries[0]
        # to find the subdivision we need the country?
        # FixMe: Just junk the field value for now.
        Subdivision = proteus.Model.get('country.subdivision')
        return None

    assert len(lElts) != 0, \
           "ERROR: No instance of %s found named '%s'" % (sRelation, uValue,)
    assert len(lElts) == 1, \
           "ERROR: Too many instances of %s found named '%s'" % (sRelation, uValue,)
    return lElts[0]
