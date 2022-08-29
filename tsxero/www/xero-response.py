import frappe
from frappe import _

def get_context(context):
    context.test = "Hollo World"
    print('context.test--------------------------------------------------', context.test)
    return context
