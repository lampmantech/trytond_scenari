# -*- encoding: utf-8 -*-

@works32 @works34 @works36
Feature:    /n/data/TrytonOpenERP/src/Tryton-3.2/trytond-3.2.4/trytond/ir/

  Scenario: attachment.py
             Try to make an attachment in the form of a link
	     onto the admin user. The code works but no
	     attachment shows up on the user...

      Given Ensure that the "party" module is loaded
        And ir/attachment test
