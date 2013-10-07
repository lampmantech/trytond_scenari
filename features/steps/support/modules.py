# -*- encoding: utf-8 -*-
"""
This is support code for basic operations on modules.

"""
from proteus import Model, Wizard

def lInstallModules(lMods, oProteusConfig):
    Module = Model.get('ir.module.module')
    modules = Module.find([
        ('name', 'in', lMods),
    ])
    if not modules:
        all_module_names = [x.name for x in Module.find()]
        assert modules, "modules %r not in available modules: %r" \
          % (lMods, all_module_names,)
        
    modules = Module.find([
        ('name', 'in', lMods),
        ('state', '!=', 'installed'),
    ])
    if len(modules):
        Module.install([x.id for x in modules], oProteusConfig.context)
    modules = [x.name for x in Module.find([('state', '=', 'to install')])]
    if len(modules):
        Wizard('ir.module.module.install_upgrade').execute('upgrade')

        ConfigWizardItem = Model.get('ir.module.module.config_wizard.item')
        for item in ConfigWizardItem.find([('state', '!=', 'done')]):
            item.state = 'done'
            item.save()

    return modules

def lInstalledModules():
    Module = Model.get('ir.module.module')
    installed_modules = [m.name
        for m in Module.find([('state', '=', 'installed')])]
    return installed_modules
