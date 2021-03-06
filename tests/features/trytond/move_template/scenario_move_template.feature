# -*- encoding: utf-8 -*-

@works36    
Feature:    Run the Trytond scenario_move_template doctests
  Adapted from the file {{{trytond_account-3.6.0/tests/}}}
  [[https://github.com/lampmantech/trytond_scenari/master/raw/tests/features/trytond/move_template/scenario_move_template.rst|scenario_move_template.rst]]

  A move template allows one to configure predefined moves. 
  A Move Template is defined by the following fields
  
  * Name
  * Company
  * Keywords - The list of keywords used in the template.
  * Journal
  * Date - The date of the move. It must be leaved empty for today.
  * Description - The description of the move. The keyword values can be
    substituted using the name surrounded by braces ('{' and '}').
  * Lines - The list of template lines.
  * Active

  Move Template Keywords
      The keywords define the values asked to user to create the move based on the
      template. The fields are:
      
      * Name
      * String - The label used in the wizard form.
      * Sequence - The sequence used to order the fields in the wizard form.
      * Type - char, numeric, date, party
      * Digits - Only for numeric keyword.

  Move Line Template
      * Operation - debit or credit
      * Amount - An expression that can use any keywords to compute the amount.
      * Account
      * Party - Only for account that requires a party.
      * Description
      * Taxes - The list of template tax lines
      
  Tax Line Template
      
      * Amount - An expression that can use any keywords to compute the amount.
      * Code - The tax code to use.
      * Tax

  A wizard to create moved base on templates is available in the *Entries* menu.
  The templates are also available as actions when opening a journal.
    
  Scenario: Setup the tests of the module named "move_template"

      Given Create database with pool.test set to True
        And Ensure that the "account_invoice" module is loaded
        And Set the default feature data
       Then the "account_invoice" module is in the list of loaded modules

  Scenario: Setup the test company for the feature, with a sales tax

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a chart of accounts \
            from template "Minimal Account Chart" \
            with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"
        And Create a tax named "10% Sales Tax" with fields
            | name                  | value             |
            | description           | 10% Sales Tax     |
            | type                  | percentage        |
            | rate                  | .10               |
            | invoice_base_code     | invoice base      |
            | invoice_tax_code      | invoice tax       |
            | credit_note_base_code | credit note base  |
            | credit_note_tax_code  | credit note tax   |

  Scenario: Make a move template and then define the Move Template Keywords
          
      Given Create a MoveTemplate named "Test Move Template" on Journal coded "CASH"
        And Add keywords to a MoveTemplate named "Test Move Template" with description "{party} - {description}" and |name|string|type|digits| following
            | name        | string      | type    | digits |
            | party       | Party       | party   |        |
            | description | Description | char    |        |
            | amount      | Amount      | numeric |      2 |
            | rate        | Tax Rate    | numeric |      3 |
            | date        | Date        | char    |        | 
  
  Scenario: Populate the Move Line Template

      Given T/AIMT Add lines to a MoveTemplate named "Test Move Template" with Tax "10% Sales Tax" and |amount|account|tax|party|operation| following
            | amount               | account         | tax  | party | operation |
            | amount               | payable         |      | party | credit    |
            | amount / 1.1         | expense         | base | party | debit     |
            | amount * (1 - 1/1.1) | invoice_account | tax  | party | debit     |

  Scenario:  Run the template instance

      Given Create a move from a MoveTemplate named "Test Move Template" on date "TODAY" with |name|value| keywords following
            | name                 | value                    |
            | party                | Supplier                 |
            | description          | Test Move Template TODAY |
            | amount               | 12.24                    |

       Then T/AIMT Check the moves with the description "Supplier - Test Move Template TODAY" and Tax named "10% Sales Tax"
