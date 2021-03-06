# -*- encoding: utf-8 -*-

@wip
Feature:    Run the Trytond scenario_account_stock_anglo_saxon doctests with the
    "product_cost_fifo" module loaded and with a cost_price_method of "fifo.
    This FAILS on the asserts, as it should for, now because it is a copy
    changed to use FIFO, but the accounting results have not yet been updated.

  Scenario: Run the tests of the module named "product_cost_fifo"

      Given Create database with pool.test set to True
        And Ensure that the "account_stock_anglo_saxon" module is loaded
        And Ensure that the "product_cost_fifo" module is loaded
        And Ensure that the "sale" module is loaded
        And Ensure that the "purchase" module is loaded
        And Set the default feature data
# These are in by trytond_account_stock_continental/account.xml
# which is pulled in by trytond_account_stock_anglo_saxon
        And Set the feature data with values
            | name                                  | value                	|
            | account.template,main_cogs            | COGS                 	|
            | account.template,stock                | Stock                	|
            | account.template,stock_customer       | Stock Customer       	|
            | account.template,stock_lost_found     | Stock Lost and Found 	|
            | account.template,stock_production     | Stock Production     	|
            | account.template,stock_supplier       | Stock Supplier       	|
       Then the "account_stock_anglo_saxon" module is in the list of loaded modules

  Scenario: Create the company to test the module named "product_cost_fifo"

      Given Create the company with default COMPANY_NAME and Currency code "EUR"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"
        And Create a saved instance of "product.category" named "Category"
        And Create a party named "Customer" with an account_payable attribute


  Scenario: Buy the products from the supplier, testing the module named "product_cost_fifo"

      Given Create a user named "Accountant" with the fields
            | name	| value		  	|
            | login	| accountant	  	|
            | password	| accountant	  	|
            | group	| Account	  	|
        And Create a PaymentTerm named "Direct" with "0" days remainder
        And Create a ProductTemplate named "product" with stock accounts \
	    from features from a ProductCategory named "Category" \
	    with |name|value| fields
            | name              | value 	|
            | type	      | goods 	|
            | cost_price_method | fifo  	|
            | purchasable       | True  	|
            | salable 	      | True  	|
            | list_price 	      | 10    	|
            | cost_price 	      | 5     	|
            | delivery_time     | 0     	|
            | default_uom	      | Unit  	|
            | account_expense   | Main Expense 	|
            | account_revenue   | Main Revenue 	|
            | account_cogs      | Main Expense 	|
        And T/ASAS/SASAS Create products of type "goods" \
	    from the ProductTemplate named "product" with fields
            | name                | cost_price_method | description         	|
            | product_fixed	| fifo   	    | Product Fixed       	|
            | product_average	| fifo		    | Product Average     	|
        And Create a Purchase Order with description "12 products" \
	    from supplier "Supplier" with fields
            | name              | value    	|
            | invoice_method    | shipment 	|
            | payment_term      | Direct 	 	|
            | purchase_date     | TODAY	 	|
#?	  | currency          | EUR	 	|
        And T/ASAS/SASAS Purchase products on the P. O. \
	    with description "12 products" from supplier "Supplier" \
	    with quantities
            | description  	| quantity | unit_price 	|
            | Product Fixed	| 5.0	   | 4			|
            | Product Average	| 7.0	   | 6			|
        And T/ASAS/SASAS Quote and Confirm and Process a P. O. with description "12 products" from supplier "Supplier"
        And T/ASAS/SASAS Receive 9 products from the P. O. \
	    with description "12 products" from supplier "Supplier" \
	    with quantities
            | description     | quantity 	|
            | Product Fixed   | 4.0      	|
            | Product Average | 5.0      	|
        And T/ASAS/SASAS After receiving 9 products assert the account credits and debits
# AssertionError: Expected 50.00,0.00 but got 46.00,0.00
        And T/ASAS/SASAS Open a purchase invoice to pay for what we received from the P. O. with description "12 products" to supplier "Supplier" with prices
            | description     | unit_price 	|
            | Product Fixed   | 6.00     	 	|
            | Product Average | 4.00     	 	|
        And T/ASAS/SASAS After paying for what we received assert the account credits and debits

  Scenario: Sell the products to the customer, testing the module named "product_cost_fifo"

      Given Create a sales order with description "Sell 5 products" \
      	    in Currency coded "EUR" to customer "Customer" \
	    on date "NOW" with |name|value| fields
            | name              | value    	|
            | invoice_method    | shipment 	|
            | payment_term      | Direct   	|
        And Sell Products on the S. O. with description "Sell 5 products" to customer "Customer" with |description|quantity| fields
            | description     | quantity 	|
            | Product Fixed   | 2.0      	|
            | Product Average | 3.0      	|
        And Ship the products on "TODAY" of the S. O. \
	    with description "Sell 5 products" to customer "Customer"
        And T/ASAS/SASAS After shipping to customer \
	    assert the account credits and debits
        And Post customer Invoice for the S. O. \
	    with description "Sell 5 products" to customer "Customer"
        And T/ASAS/SASAS After posting the invoice to customer \
	    assert the account credits and debits
        And T/ASAS/SASAS Create an Invoice to supplier "Supplier" \
	    with PaymentTerm "Direct" by an accountant with quantities
            | description     | quantity	| unit_price 	|
            | Product Fixed   | 5.0      	| 4.00	     	|

