from . import __version__ as app_version

app_name = "tsxero"
app_title = "Xero Integration"
app_publisher = "Techseria"
app_description = "Techseria Xero Integration with ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@techseria.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tsxero/css/tsxero.css"
# app_include_js = "/assets/tsxero/js/tsxero.js"
app_include_js = "/assets/tsxero/fontawesome/js/custom/item.js"
app_include_js = "/assets/tsxero/fontawesome/js/custom/payment_entry.js"
# app_include_js = "/assets/tsxero/fontawesome/js/custom/sales_taxes_and_charges_template.js"

# include js, css files in header of web template
# web_include_css = "/assets/tsxero/css/tsxero.css"
# web_include_js = "/assets/tsxero/js/tsxero.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tsxero/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"Item" : "public/fontawesome/js/custom/item_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tsxero.install.before_install"
# after_install = "tsxero.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tsxero.uninstall.before_uninstall"
# after_uninstall = "tsxero.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tsxero.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Customer": {
		"after_insert": "tsxero.api.create_customer_in_xero",
		"on_update": "tsxero.api.create_customer_in_xero"
	},
	"Supplier": {
		"after_insert": "tsxero.api.create_supplier_in_xero",
		"on_update": "tsxero.api.create_supplier_in_xero"
	},
	"Sales Invoice": {
		"after_insert": "tsxero.api.create_sales_invoice_in_xero",
		"on_update": "tsxero.api.create_sales_invoice_in_xero",
		"on_submit": "tsxero.api.popup_msg"
	},
	"Purchase Invoice": {
		"after_insert": "tsxero.api.create_purchase_invoice_in_xero",
		"on_update": "tsxero.api.create_purchase_invoice_in_xero",
  		"on_submit": "tsxero.api.popup_msg"
	},
	"Payment Entry": {
		"on_update": "tsxero.api.erp_payment_entry_to_xero",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tsxero.tasks.all"
# 	],
# 	"daily": [
# 		"tsxero.tasks.daily"
# 	],
# 	"hourly": [
# 		"tsxero.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tsxero.tasks.weekly"
# 	]
# 	"monthly": [
# 		"tsxero.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "tsxero.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tsxero.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tsxero.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tsxero.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
