# -*- encoding: utf-8 -*-

@wip
Feature:    Run the Trytond scenario_move_template doctests
  Adapted from the file 
  trytond_account_asset-3.6.2/tests/scenario_account_asset.rst
  
  The account_asset module adds the depreciation of fixed assets.
  
  Asset
  
  An Asset defines how an asset is depreciated. It is mainly defined by
  
  * Product (of type "Assets").
  * Journal.
  * Value and Residual Value.
  * Start and End Date.
  * Depreciation Method
    * Linear
  * Frequency
    * Monthly
    * Yearly
  * Lines.
  
  The asset can be in one of this states
  
  * Draft
  
    The depreciation lines can be created.
  
  * Running
  
    The accounting moves of depreciation lines are posted.
  
  * Closed
  
    The value of the asset has been completly depreciated.
  
  A wizard "Create Assets Moves" allows to post all accounting move up to a date.
  
  Asset Line
  
  An Asset Line defines for a date the value to depreciate.
  
  Scenario: Setup the tests of the module named "account_asset"

      Given Create database with pool.test set to True
        And Ensure that the "account_asset" module is loaded
        And Set the default feature data
       Then the "account_asset" module is in the list of loaded modules

  Scenario: Setup the test company for the feature

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a chart of accounts \
            from template "Minimal Account Chart" \
            with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"

        Then Account Asset Scenario
