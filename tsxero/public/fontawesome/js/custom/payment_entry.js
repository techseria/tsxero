frappe.ui.form.on('Payment Entry', {
    refresh(frm) {
        frm.add_custom_button(__("Xero Payment to ERP Import"), function()  {
            frappe.call({
                method: "tsxero.api.xero_payment_entry_to_erp",
                callback: function(r){
                    frappe.msgprint("Imported <b>"+ r.message.import_payment + " payment</b> successfully!");
                }
            });
        });
	}
})