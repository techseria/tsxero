// Copyright (c) 2022, Techseria and contributors
// For license information, please see license.txt

frappe.ui.form.on('Xero Configuration Settings', {
	refresh: function(frm) {
		var url = window.location.href;
		var url2 = url.split('/');
		frm.doc.redirect_url = url2[0]+'//'+url2[1]+url2[2]+"/xero-response";
		function ConnectButton(){
			frm.add_custom_button(__('Connect'), function() {
				window.open(`https://login.xero.com/identity/connect/authorize?` +
                `response_type=code` + `&client_id=` + frm.doc.client_id +
                `&redirect_uri=` + frm.doc.redirect_url + `&scope=` + // Dynamic not set for redirect_uri
                frm.doc.scopes + `&state=12345`, 'popup','width=600,height=600');
				frappe.msgprint("Wait for 30 sec.. Do not any action");
				setTimeout(function () { }, 30000);
				frappe.call({
					"method" : "tsxero.xero_integration.doctype.xero_configuration_settings.xero_configuration_settings.get_conf_data",
					"args" : {
						name : frm.doc.name,
					},
					"callback" : function(r){
						if(r.message.status_code == '200'){
							CustomerImportButton();
							SupplierImportButton();
							RefreshTokenButton();
							frm.remove_custom_button('Connect');
							frappe.msgprint("Connection success! Please close the alert message");
						}
						else{
							frappe.throw(__("Connection failed. Please try again"));
						}
					}
				});
			});
		}
		function CustomerImportButton(){
			frm.add_custom_button(__('Xero Customer Import'), function() {
				frappe.call({
					"method" : "tsxero.xero_integration.doctype.xero_configuration_settings.xero_configuration_settings.ContactsAPI",
					"args" : {
						name : frm.doc.name,
						flag : 'IsCustomer'
					},
					"callback" : function(r){
						if(r.message.status == 'Success'){
							frappe.msgprint("Imported <b>"+ r.message.import_customer + " customers</b> successfully!");
						}
						else{
							frappe.throw(__('Import failed. Please refresh the token'));
						}
					}
				});
			});
		}
		function SupplierImportButton(){
			frm.add_custom_button(__('Xero Supplier Import'), function() {
				frappe.call({
					"method" : "tsxero.xero_integration.doctype.xero_configuration_settings.xero_configuration_settings.ContactsAPI",
					"args" : {
						name : frm.doc.name,
						flag : 'IsSupplier'
					},
					"callback" : function(r){
						if(r.message.status == 'Success'){
							frappe.msgprint("Imported <b>"+ r.message.import_customer + " suppliers</b> successfully!");
						}
						else{
							frappe.throw(__('Import failed. Please refresh the token'));
						}
					}
				});
			});
		}
		function RefreshTokenButton(){
			frm.add_custom_button(__('Refresh Token'), function() {
				frappe.call({
					"method" : "tsxero.xero_integration.doctype.xero_configuration_settings.xero_configuration_settings.xero_refresh_token",
					"args" : {
						name : frm.doc.name,
					},
					"callback" : function(r){
						if(r.message != 'Failed'){
							frappe.msgprint("Refresh token successfully!");
						}
						else{
							ConnectButton();
							frm.remove_custom_button('Refresh Token');
							frm.remove_custom_button('Xero Supplier Import');
							frm.remove_custom_button('Xero Customer Import');
							frappe.throw(__('Refresh token failed. Please connect again'));
						}
					}
				});
			});
		}
		if (frm.doc.token_status === "0"){
			ConnectButton();
		}
		else if (frm.doc.token_status === "1"){
			CustomerImportButton();
			SupplierImportButton();
			RefreshTokenButton();
		}
		
	}
});
