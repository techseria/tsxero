frappe.ui.form.on('Item', {
    refresh(frm) {
        frm.add_custom_button(__("Xero Items Import"), function()  {
            frappe.call({
                method: "tsxero.api.import_xero_items",
                callback: function(r){
                    frappe.msgprint("Imported <b>"+ r.message.import_items + " items</b> successfully!");
                }
            });
        });
	}
})

