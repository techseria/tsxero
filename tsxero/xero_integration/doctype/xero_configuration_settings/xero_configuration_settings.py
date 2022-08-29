# Copyright (c) 2022, Techseria and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import base64
import requests
import time



class XeroConfigurationSettings(Document):
    pass

@frappe.whitelist()
def get_conf_data(name):
    get_configuration = frappe.get_doc('Xero Configuration Settings', {'name':name}, cache=True)
    get_client_id = get_configuration.client_id
    get_client_secret = get_configuration.client_secret
    get_redirect_uri = get_configuration.redirect_url
    b64_id_secret = base64.b64encode(bytes(get_client_id + ':' + get_client_secret, 'utf-8'))
    TokenAccess(get_client_id, get_redirect_uri, b64_id_secret)
    auth_code = frappe.cache().get_value('auth_code')
    if auth_code:
        frappe.cache().set_value('auth_code', "")
        status = frappe.get_doc('Xero Configuration Settings', {'client_id':get_client_id})
        status.token_status = 1
        status.save()
        return {"status_code":"200"}
    else:
        return {"status_code":"403"}

def TokenAccess(get_client_id, get_redirect_uri, b64_id_secret):
    time.sleep(30)
    auth_code = frappe.cache().get_value('auth_code')
    if auth_code:
        exchange_code_url = 'https://identity.xero.com/connect/token'
        response = requests.post(exchange_code_url,
                                headers={'Authorization': 'Basic ' + b64_id_secret.decode('ascii')},
                                data={'grant_type': 'authorization_code',
                                    'code': auth_code,
                                    'redirect_uri': get_redirect_uri}
                                )
        json_res = response.json()
        get_Doc = frappe.get_doc('Xero Configuration Settings', {'client_id':get_client_id})
        get_Doc.refresh_token = json_res['refresh_token']
        get_Doc.access_token = json_res['access_token']
        get_Doc.save()
    
def Connection(token):
    connect = 'https://api.xero.com/connections'

    res = requests.get(connect, headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})

    json_ress = res.json()
    tenantId = ""
    for t in json_ress:
        if 'tenantId' in t:
            tenantId = t['tenantId']
    return tenantId

@frappe.whitelist()
def xero_refresh_token(name):
    old_refresh_token = frappe.get_value('Xero Configuration Settings', {'name':name}, 'refresh_token')
    get_client_id = frappe.get_value('Xero Configuration Settings', {'name':name}, 'client_id')
    get_client_secret = frappe.get_value('Xero Configuration Settings', {'name':name}, 'client_secret')
    b64_id_secret = base64.b64encode(bytes(get_client_id + ':' + get_client_secret, 'utf-8'))
    url = 'https://identity.xero.com/connect/token'
    response = requests.post(url,
                             headers={
                                 'Authorization': f"Basic {b64_id_secret.decode('ascii')}",
                                 'Content-Type': 'application/x-www-form-urlencoded'
                             },
                             data={
                                 'grant_type': 'refresh_token',
                                 'client_id': get_client_id,
                                 'refresh_token': old_refresh_token
                             })
    if response.status_code == 200:
        response_dict = response.json()
        new_access_token = response_dict['access_token']
        get_Doc = frappe.get_doc('Xero Configuration Settings', {'client_id':get_client_id})
        get_Doc.access_token = new_access_token
        get_Doc.save()
        return [new_access_token]
    else:
        status = frappe.get_doc('Xero Configuration Settings', {'client_id':get_client_id})
        status.token_status = 0
        status.save()
        return "Failed"    
    
@frappe.whitelist()
def ContactsAPI(name, flag):
    ContactUrl = f'https://api.xero.com/api.xro/2.0/Contacts?where={flag}=true'
    new_tokens = frappe.get_value('Xero Configuration Settings', {'name':name}, 'access_token')
    xero_tenant_id = Connection(new_tokens)
    conRes = requests.get(ContactUrl,
                          headers={'xero-tenant-id': xero_tenant_id,
                                   'Authorization': f'Bearer {new_tokens}',
                                   'Accept': 'application/json'
                                   }
                          )
    if conRes.status_code == 200:
        customers = ImportXeroCustomerToErp(conRes.json()['Contacts'], flag)
        return {"status": "Success", "import_customer": customers}
    else:
        return {"status": "Failed"}
    
def ImportXeroCustomerToErp(Customers, flag):
    default_company = frappe.get_list('Company', ['Country'])
    import_customer = 0
    for customer in Customers:
        already_exiest_customer = frappe.db.exists("Customer", customer['Name'])
        already_exiest_supplier = frappe.db.exists("Supplier", customer['Name'])
        if not already_exiest_customer and flag == "IsCustomer":
            new_customer = frappe.new_doc('Customer')
            if 'CompanyNumber' not in customer:
                new_customer.company_registration_number = ""
            else:
                new_customer.company_registration_number = customer['CompanyNumber']
            if 'TaxNumber' not in customer:
                new_customer.tax_id = ""
            else:
                new_customer.tax_id = customer['TaxNumber']
            if 'Currency' not in customer:
                new_customer.default_currency = "GBP"
            else:
                new_customer.default_currency = str(customer['Currency']).split(' ')[0]
            if 'Website' not in customer:
                new_customer.website = ""
            else:
                new_customer.website = customer['Website']
            
            new_customer.customer_name = customer['Name']
            new_customer.customer_type = "Company"
            new_customer.customer_group = "All Customer Groups"
            new_customer.territory = "United Kingdom"
            
            new_customer.save()
                
            address_and_contact(customer, default_company, "Customer")
                    
            import_customer += 1
            
        elif not already_exiest_supplier and flag == 'IsSupplier':
            new_supplier = frappe.new_doc('Supplier')
            
            if 'CompanyNumber' not in customer:
                new_supplier.company_registration_number = ""
            else:
                new_supplier.company_registration_number = customer['CompanyNumber']
            if 'TaxNumber' not in customer:
                new_supplier.tax_id = ""
            else:
                new_supplier.tax_id = customer['TaxNumber']
            if 'Currency' not in customer:
                new_supplier.default_currency = "GBP"
            else:
                new_supplier.default_currency = str(customer['Currency']).split(' ')[0]
            if 'Website' not in customer:
                new_supplier.website = ""
            else:
                new_supplier.website = customer['Website']
                
            new_supplier.supplier_name = customer['Name']
            new_supplier.supplier_type = "Company"
            new_supplier.supplier_group = "All Supplier Groups"
            new_supplier.country = default_company[0]['Country']
            
            new_supplier.save()
            
            address_and_contact(customer, default_company, "Supplier")
                    
            import_customer += 1
    return import_customer
               
def address_and_contact(customer, default_company, doctype):
    new_contact = frappe.new_doc('Contact')
    for contact in customer['Phones']:
        if 'FirstName' not in customer:
            customer['FirstName'] = ""
            
        if contact['PhoneNumber'] and (customer['FirstName'] or customer['Name']):
            already_exists_contact = frappe.db.exists('Contact', {'first_name':customer['FirstName'] or customer['Name']})
            if not already_exists_contact:
                new_contact.first_name = customer['FirstName'] or customer['Name']
                if 'LastName' not in customer:
                    new_contact.last_name = ""
                else:
                    new_contact.last_name = customer['LastName']
                    
                if 'EmailAddress' in customer:
                    if customer['EmailAddress']:
                        new_contact.append('email_ids', {
                        "email_id": customer['EmailAddress'],
                        "is_primary": 0,
                        })
                
                new_contact.append('phone_nos', {
                    "phone": contact['PhoneNumber'],
                    "is_primary_phone": 0,
                    "is_primary_mobile_no": 0,
                })
                
                new_contact.append("links", {
                    "link_doctype": doctype,
                    "link_name": customer['Name'],
                    "link_title": customer['Name'],
                })
                
                new_contact.save()
            
    for address in customer['Addresses']:
        new_address = frappe.new_doc('Address')
        if 'AddressLine1' not in address:
            address['AddressLine1'] = ""
        if address['AddressLine1'] and address['City']:
            already_exists_address = frappe.db.exists('Address', {'address_title':customer['Name']})
            if not already_exists_address:
                new_address.address_line1 = address['AddressLine1']
                new_address.city = address['City']
            
                if 'AddressLine2' not in address:
                    new_address.address_line2 = ""
                else:
                    new_address.address_line2 = address['AddressLine2']
                
                new_address.address_title = customer['Name']
                new_address.address_type = "Billing"
                if 'Region' not in address:
                    new_address.state = ""
                else:
                    new_address.state = address['Region']
                if address['Country']:
                    new_address.country = address['Country']
                    new_address.county = address['Country']
                else:
                    new_address.country = default_company[0]['Country']
                if 'PostalCode' not in address:
                    new_address.pincode = ""
                else:
                    new_address.pincode = address['PostalCode']
                    
                
                new_address.append("links", {
                    "link_doctype": doctype,
                    "link_name": customer['Name'],
                    "link_title": customer['Name'],
                })
                new_address.save()


