import frappe
import requests
from datetime import datetime
import re
from tsxero.xero_integration.doctype.xero_configuration_settings.xero_configuration_settings import Connection

@frappe.whitelist(allow_guest=True)
def auth_code(url):
    start_num = url.find('code=') + len('code=')
    end_num = url.find('&scope')
    auth_code = url[start_num:end_num]
    frappe.cache().set_value('auth_code', auth_code)
    
def create_customer_in_xero(doc, method):
    ContactUrl = 'https://api.xero.com/api.xro/2.0/Contacts'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    dynamic_link_for_address = frappe.get_list('Dynamic Link', {'link_name':doc.name, 'link_doctype':'Customer', 'parenttype':'Address'}, {'*'}, ignore_permissions=True)
    dynamic_link_for_contact = frappe.get_list('Dynamic Link', {'link_name':doc.name, 'link_doctype':'Customer', 'parenttype':'Contact'}, {'*'}, ignore_permissions=True)
    
    data = {}
    
    total_address = []
    for address in dynamic_link_for_address:
        total_address.append(address.parent)
        
    total_contact = []
    for contact in dynamic_link_for_contact:
        total_contact.append(contact.parent)
    
    addresses = []
    
    address_type = ['POBOX', 'STREET']
    j = 0
    for field in total_address:
        get_address = frappe.get_doc('Address', field)
        addresses.append({
            "AddressType":address_type[j],
            "AddressLine1":get_address.address_line1,
            "AddressLine2": get_address.address_line2,
            "City": get_address.city,
            "Region": get_address.state,
            "PostalCode": get_address.pincode,
            "Country": get_address.country
        })
        j+=1
        
    phones = []
    
    phonetype = ['DEFAULT', 'MOBILE', 'FAX', 'DDI']
    for field in total_contact:
        get_contact = frappe.get_doc('Contact', field)
        data.update(
            {
            "FirstName":get_contact.first_name,
            "LastName":get_contact.last_name,
            "EmailAddress":get_contact.email_id
            }
            )
        i = 0
        for number in get_contact.phone_nos:
            phones.append({
                "PhoneNumber":number.phone,
                "PhoneType":phonetype[i]
            })
            i+=1
            
    data.update({
        "Name": doc.customer_name, 
        "CompanyNumber": doc.company_registration_number, 
        "TaxNumber": doc.tax_id,
        "DefaultCurrency": doc.default_currency,
        "Addresses": addresses,
        "Phones": phones,
        "Website": doc.website
        })

    conRes = requests.post(ContactUrl,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Content-Type': 'application/json'
                                   },
                          json=data,
                          )
    print('conRes.status_code--------------------------', conRes.status_code)
    
def create_supplier_in_xero(doc, method):
    ContactUrl = 'https://api.xero.com/api.xro/2.0/Contacts'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    dynamic_link_for_address = frappe.get_list('Dynamic Link', {'link_name':doc.name, 'link_doctype':'Supplier', 'parenttype':'Address'}, {'*'}, ignore_permissions=True)
    dynamic_link_for_contact = frappe.get_list('Dynamic Link', {'link_name':doc.name, 'link_doctype':'Supplier', 'parenttype':'Contact'}, {'*'}, ignore_permissions=True)
    
    data = {}
    
    total_address = []
    for address in dynamic_link_for_address:
        total_address.append(address.parent)
        
    total_contact = []
    for contact in dynamic_link_for_contact:
        total_contact.append(contact.parent)
    
    addresses = []
    address_type = ['POBOX', 'STREET']
    j = 0
    for field in total_address:
        get_address = frappe.get_doc('Address', field)
        addresses.append({
            "AddressType":address_type[j],
            "AddressLine1":get_address.address_line1,
            "AddressLine2": get_address.address_line2,
            "City": get_address.city,
            "Region": get_address.state,
            "PostalCode": get_address.pincode,
            "Country": get_address.country
        })
        j+=1
        
    phones = []
    
    phonetype = ['DEFAULT', 'MOBILE', 'FAX', 'DDI']
    for field in total_contact:
        get_contact = frappe.get_doc('Contact', field)
        data.update(
            {
            "FirstName":get_contact.first_name,
            "LastName":get_contact.last_name,
            "EmailAddress":get_contact.email_id
            }
            )
        i = 0
        for number in get_contact.phone_nos:
            phones.append({
                "PhoneNumber":number.phone,
                "PhoneType":phonetype[i]
            })
            i+=1
            
    data.update({
        "Name": doc.supplier_name, 
        "CompanyNumber": doc.company_register_number, 
        "TaxNumber": doc.tax_id,
        "DefaultCurrency": doc.default_currency,
        "Addresses": addresses,
        "Phones": phones,
        "Website": doc.website
        })
    
    conRes = requests.post(ContactUrl,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Content-Type': 'application/json'
                                   },
                          json=data,
                          )

def create_sales_invoice_in_xero(doc, method):
    SalesInvoice = 'https://api.xero.com/api.xro/2.0/Invoices'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    
    ContactsAPI = f'https://api.xero.com/api.xro/2.0/Contacts?where=Name="{doc.customer}"'
    ContactResponse = requests.get(ContactsAPI,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )
    data = {}
    if len(ContactResponse.json()['Contacts']) > 0:
        ContactID = ContactResponse.json()['Contacts'][0]['ContactID']
        Name = ContactResponse.json()['Contacts'][0]['Name']
        lineItems = []
        
        for item in doc.items:
            lineItems.append(
                {
                    'Description': item.description,
                    "Quantity": item.qty,
                    "UnitAmount": item.rate,
                    "DiscountRate": doc.additional_discount_percentage,
                    "AmountGBP": item.rate,
                    "AccountCode": "200"
                }
                )
    
        data.update({
            "Type": "ACCREC",
            "Contact": {'ContactID': ContactID, 'Name': Name},
            "DateString": doc.posting_date,
            "DueDate": doc.due_date,
            "CurrencyCode": doc.currency,
            "SubTotal": doc.total,
            "Status": doc.status,
            "TotalTax": doc.total_taxes_and_charges,
            "Total": doc.grand_total,
            "AmountDue": doc.grand_total,
            "AmountPaid": int(doc.grand_total) - int(doc.outstanding_amount),
            "CurrencyRate": 1,
            "lineItems": lineItems,
            "LineAmountTypes": "Exclusive"
        })
        
    print('method-----------------', method)
    
    if method == 'after_insert':
        conRes = requests.post(SalesInvoice,
                            headers={'xero-tenant-id': xero_tenant_id,
                                    'Authorization': f'Bearer {new_tokens}',
                                    'Content-Type': 'application/json'
                                    },
                            json=data,
                            )
        xero_invoice_number = re.findall(r"\<InvoiceNumber>(.*?)\<\/InvoiceNumber\>", str(conRes.text))
        xero_invoice_id = re.findall(r"\<InvoiceID>(.*?)\<\/InvoiceID\>", str(conRes.text))
        doc.update({'xero_invoice_number':xero_invoice_id[0] + ', ' + xero_invoice_number[0]})
        doc.save()
    else:
        if len(ContactResponse.json()['Contacts']) > 0:
            InvoiceID = str(doc.xero_invoice_number).split(', ')[0]
            conRes = requests.post(SalesInvoice+f'/{InvoiceID}',
                                headers={'xero-tenant-id': xero_tenant_id,
                                        'Authorization': f'Bearer {new_tokens}',
                                        'Content-Type': 'application/json'
                                        },
                                json=data,
                                )
       
def create_purchase_invoice_in_xero(doc, method):
    PurchaseInvoice = 'https://api.xero.com/api.xro/2.0/Invoices'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    
    ContactsAPI = f'https://api.xero.com/api.xro/2.0/Contacts?where=Name="{doc.supplier}"'
    ContactResponse = requests.get(ContactsAPI,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )
    
    data = {}
    if len(ContactResponse.json()['Contacts']) > 0:
        ContactID = ContactResponse.json()['Contacts'][0]['ContactID']
        Name = ContactResponse.json()['Contacts'][0]['Name']
        lineItems = []
        
        for item in doc.items:
            lineItems.append(
                {
                    'Description': item.description,
                    "Quantity": item.qty,
                    "UnitAmount": item.rate,
                    "AmountGBP": item.rate,
                    "AccountCode": "300"
                }
                )
        
        data.update({
            "Type": "ACCPAY",
            "Contact": {'ContactID': ContactID, 'Name': Name},
            "DateString": doc.posting_date,
            "DueDateString": doc.due_date,
            "Status": doc.status,
            "CurrencyCode": doc.currency,
            "SubTotal": doc.total,
            "TotalTax": doc.total_taxes_and_charges,
            "Total": doc.total,
            "AmountDue": doc.grand_total,
            "AmountPaid": int(doc.grand_total) - int(doc.outstanding_amount),
            "CurrencyRate": 1,
            "lineItems": lineItems,
            "LineAmountTypes": "Exclusive"
        })
    
    if method == 'after_insert':
        conRes = requests.post(PurchaseInvoice,
                            headers={'xero-tenant-id': xero_tenant_id,
                                    'Authorization': f'Bearer {new_tokens}',
                                    'Content-Type': 'application/json'
                                    },
                            json=data,
                            )
        xero_invoice_id = re.findall(r"\<InvoiceID>(.*?)\<\/InvoiceID\>", str(conRes.text))
        doc.update({'xero_invoice_number':xero_invoice_id[0]})
        doc.save()
    else:
        if len(ContactResponse.json()['Contacts']) > 0:
            InvoiceID = str(doc.xero_invoice_number).split(', ')[0]
            conRes = requests.post(PurchaseInvoice+f'/{InvoiceID}',
                                headers={'xero-tenant-id': xero_tenant_id,
                                        'Authorization': f'Bearer {new_tokens}',
                                        'Content-Type': 'application/json'
                                        },
                                json=data,
                                )
            
            print('conRes----------------', conRes.status_code)
        
@frappe.whitelist()
def import_xero_items():
    Items = 'https://api.xero.com/api.xro/2.0/Items'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    
    conRes = requests.get(Items,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )

    import_items = 0
    for item in conRes.json()['Items']:
        already_exists = frappe.db.exists("Item", {"item_code": item['Code']})
        
        if not already_exists:
            new_item = frappe.new_doc('Item')
            new_item.item_code = item['Code']
            new_item.item_name = item["Name"]
            new_item.item_group = "All Item Groups"
            new_item.description = item["Description"]
            new_item.is_purchase_item = 1
            new_item.is_salse_item = 1
            new_item.save()
            import_items += 1
            
    return {"import_items": import_items}

@frappe.whitelist()
def xero_payment_entry_to_erp():
    PaymentEntry = 'https://api.xero.com/api.xro/2.0/Payments'
    Accounts = 'https://api.xero.com/api.xro/2.0/Accounts'
    get_l = frappe.get_list("Xero Configuration Settings")
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    
    conRes = requests.get(PaymentEntry,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )
    
    account = requests.get(Accounts,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )
    
    account_code = account.json()['Accounts']

    import_payment = 0
    for payment in conRes.json()['Payments']:
        InvoiceID_with_InvoiceNum = f"{payment['Invoice']['InvoiceID']}, {payment['Invoice']['InvoiceNumber']}"
        
        already_exists_sales_inv = frappe.db.exists("Sales Invoice", {"xero_invoice_number": InvoiceID_with_InvoiceNum})
        already_exists_purchase_inv = frappe.db.exists("Purchase Invoice", {"xero_invoice_number": payment['Invoice']['InvoiceID']})
        
        if (already_exists_sales_inv != None or already_exists_purchase_inv != None) and payment['Status'] != "DELETED":
            
            print("already_exists_purchase_inv-----------", already_exists_purchase_inv)
            if already_exists_sales_inv != None:
                get_erp_invoice = frappe.get_doc('Sales Invoice', {'xero_invoice_number':InvoiceID_with_InvoiceNum})
            else:
                get_erp_invoice = frappe.get_doc('Purchase Invoice', {'xero_invoice_number':payment['Invoice']['InvoiceID']})
            print('get_erp_invoice----------------', get_erp_invoice)
            print("payment['PaymentID']-------------------", payment['PaymentID'])
            
            
            payment_entry_already_exists = frappe.db.exists('Payment Entry', {'xero_payment_id':payment['PaymentID']})
            print('payment------', payment['Amount'])
            print('payment_entry_already_exists-----------', payment_entry_already_exists)
            
            
            company_abbr = frappe.get_value('Company', get_erp_invoice.company, 'abbr')
            if get_erp_invoice.name != None and payment_entry_already_exists == None:
                payment_entry = frappe.new_doc('Payment Entry')
                if payment['PaymentType'] == 'ACCRECPAYMENT':
                    payment_entry.payment_type = 'Receive'
                    payment_entry.party_type = 'Customer'
                    payment_entry.append('references', {
                        'reference_doctype': 'Sales Invoice',
                        'reference_name': get_erp_invoice.name,
                        'total_amount': payment['Amount'],
                        'allocated_amount': payment['Amount'],
                    })
                elif payment['PaymentType'] == 'ACCPAYPAYMENT':
                    payment_entry.payment_type = 'Pay'
                    payment_entry.party_type = 'Supplier'
                    payment_entry.append('references', {
                        'reference_doctype': 'Purchase Invoice',
                        'reference_name': get_erp_invoice.name,
                        'total_amount': payment['Amount'],
                        'allocated_amount': payment['Amount'],
                    })
                
                code = 0
                if str(account_code[0]['Code']).startswith("090"):
                    code = '90'
                elif str(account_code[0]['Code']).startswith("091"):
                    code = '91'
                else:
                    code = account_code[0]['Code']
                
                date = re.findall(r"\((.*?)\+", payment['Date'])
                dt_object = datetime.fromtimestamp(int(date[0])/1000)
                payment_entry.posting_date = dt_object
                payment_entry.company = get_erp_invoice.company
                payment_entry.party = payment['Invoice']['Contact']['Name']
                payment_entry.party_name = payment['Invoice']['Contact']['Name']
                payment_entry.paid_to = code + ' - ' + account_code[0]['Name'] + f' - {company_abbr}'
                payment_entry.paid_to_account_currency = payment['Invoice']['CurrencyCode']
                payment_entry.paid_from_account_currency = payment['Invoice']['CurrencyCode']
                payment_entry.paid_amount = payment['Amount']
                payment_entry.total_allocated_amount = payment['Amount']
                payment_entry.total_taxes_and_charges = get_erp_invoice.total_taxes_and_charges
                payment_entry.received_amount = payment['Amount']
                if "Reference" not in payment:
                    payment_entry.reference_no = 'Payment to xero'
                else:
                    payment_entry.reference_no = payment['Reference']
                payment_entry.reference_date = dt_object
                payment_entry.source_exchange_rate = 1
                payment_entry.target_exchange_rate = 1
                payment_entry.xero_payment_id = payment['PaymentID']
                print("payment['Amount']-------------", payment['Amount'])
                payment_entry.submit()
                import_payment += 1
    
    return {'import_payment': import_payment}

@frappe.whitelist()
def erp_payment_entry_to_xero(doc, method):
    if doc.xero_payment_id == None:
        PaymentEntry = 'https://api.xero.com/api.xro/2.0/Payments'
        get_l = frappe.get_list("Xero Configuration Settings")
        new_tokens = frappe.get_value('Xero Configuration Settings', {'name':get_l[0]['name']}, 'access_token')
        xero_tenant_id = Connection(new_tokens)
        
        data = {}
        invoice = {}
        contact = {}
        
        invoice_number = doc.references[0].reference_name
        
        code = str(doc.paid_to).split(' - ')[0]
        GetAccount = ""
        if code == "90":
            GetAccount = 'https://api.xero.com/api.xro/2.0/Accounts?where=Code="090"'
        elif code == "91":
            GetAccount = 'https://api.xero.com/api.xro/2.0/Accounts?where=Code="091"'
        else:
            GetAccount = f'https://api.xero.com/api.xro/2.0/Accounts?where=Code="{code}"'

        account = requests.get(GetAccount,
                            headers={'xero-tenant-id': xero_tenant_id,
                                    'Authorization': f'Bearer {new_tokens}',
                                    'Accept': 'application/json'
                                    }
                            )
        AccRes = account.json()["Accounts"]
        
        if doc.payment_type == 'Receive':
            invoice_doc = frappe.get_doc('Sales Invoice', invoice_number)
            data.update({"PaymentType":"ACCRECPAYMENT"})
            invoice.update({"Type":"ACCREC", 
                            "InvoiceID": str(invoice_doc.xero_invoice_number).split(', ')[0],
                            "InvoiceNumber": str(invoice_doc.xero_invoice_number).split(', ')[1]
                            })
            customer = frappe.get_doc('Customer', invoice_doc.customer)
            contact.update({
                "Name": customer.customer_name
            })
        elif doc.payment_type == 'Pay':
            invoice_doc = frappe.get_doc('Purchase Invoice', invoice_number)
            data.update({"PaymentType":"ACCPAYPAYMENT"})
            invoice.update({"Type":"ACCPAY", "InvoiceID": invoice_doc.xero_invoice_number})
            supplier = frappe.get_doc('Supplier', invoice_doc.supplier)
            contact.update({
                "Name": supplier.supplier_name
            })
        
        invoice.update({
            "CurrencyCode": invoice_doc.currency,
            "Contact": contact,
        })
        
        data.update({
            "Date": doc.posting_date,
            "BankAmount": doc.paid_amount,
            "Amount": doc.paid_amount,
            "Reference": doc.reference_no,
            "CurrencyRate": 1,
            "Status": "AUTHORISED",
            "HasAccount": True,
            "Account": {"AccountID": AccRes[0]['AccountID'], "Code": AccRes[0]['Code']},
            "Invoice": invoice
        })
        
        conRes = requests.post(PaymentEntry,
                            headers={'xero-tenant-id': xero_tenant_id,
                                    'Authorization': f'Bearer {new_tokens}',
                                    'Accept': 'application/json'
                                    },
                            json=data
                            )
        
        print('conRes.json--------------------', conRes.status_code)

        payment_id = re.findall(r"\"PaymentID\"\: \"(.*?)\"", str(conRes.text))
        doc.update({'xero_payment_id': payment_id[0]})
        doc.save()

def popup_msg(doc, method):
    invoiceId = str(doc.xero_invoice_id).split(', ')
    if len(invoiceId) == 2:
        frappe.msgprint(f'This {invoiceId[1]} invoice created in xero. Please kindly check and approve in xero')
    else:
        frappe.msgprint(f'This {doc.xero_invoice_id} invoice created in xero. Please kindly check and approve in xero')
        