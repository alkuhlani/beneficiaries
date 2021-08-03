# -*- coding: utf-8 -*-
# Copyright (c) 2021, Baida and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.model.naming import set_name_by_naming_series
from frappe import _, msgprint, throw
import frappe.defaults
from frappe.utils import flt, cint, cstr, today
from frappe.desk.reportview import build_match_conditions, get_filters_cond
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts, get_dashboard_info, get_timeline_data # keep this
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from frappe.model.rename_doc import update_linked_doctypes
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta
from frappe.permissions import add_user_permission, remove_user_permission, \
	set_user_permission_if_allowed, has_permission
from frappe.utils.password import update_password as _update_password
from frappe.utils import random_string
from frappe.utils.data import add_months
from frappe.utils import cint, cstr, formatdate, flt, getdate, nowdate, get_link_to_form
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock import get_warehouse_account_map
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.accounts.utils import get_fiscal_year
class Beneficiary(Document):

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)
	# def validate(self):
	# 	self.create_beneficiary_contact()
	# 	self.create_beneficiary_user()
		# self.update_beneficiary_permissions()
	def add_return(self):
		returnben = frappe.new_doc('Beneficiary Return')
		returnben.beneficiary = self.name
		returnben.employee = self.employee
		returnben.reason = self.reason_of_return
		# returnben.autoname()
		returnben.insert()
		
	def aids_details(self):
		i=1
		for row in self.get("aid_details"):
			row.aid_no=i;
			i=i+1
		for aid in self.get("aid_details"):
			for f in range(aid.number_of_months):
				exchange_date =  add_months(aid.from_date,f)
				row = self.append('display', {})
				row.item_code=aid.item_code
				row.type=aid.type
				row.project=aid.project
				row.activity=aid.activity
				row.cost_center=aid.cost_center
				row.amount=aid.amount
				row.warehouse=aid.warehouse
				row.qty=aid.qty
				row.exchange_date=exchange_date
				row.aid_no=aid.aid_no

	# def create_beneficiary_contact(self):
	#     # create contact from beneficiary
	# 	contact = frappe.new_doc('Contact')
	# 	contact.first_name = self.beneficiary_name
	# 	contact.email_id = self.email
	# 	contact.phone = self.phone
	# 	contact.mobile_no = self.mobile
	# 	contact.is_primary_contact = 1
	# 	contact.append('links', dict(link_doctype='Beneficiary', link_name=self.name))
	# 	if self.email:
	# 		contact.append('email_ids', dict(email_id=self.email, is_primary=1))
	# 	if self.phone:
	# 		contact.append('phone_nos', dict(phone=self.phone, is_primary_mobile_no=1))
	# 	contact.flags.ignore_permissions = self.flags.ignore_permissions
	# 	contact.autoname()
	# 	if not frappe.db.exists("Beneficiary", contact.name):
	# 		contact.insert()
	# 		self.has_contact=1

	
	# 	if self.has_contact==0:
	# 		frappe.throw("Beneficiary doesn't add to contacts list",raise_exception)
		
	# 	if self.has_contact==1:
		
	# 			user = frappe.get_doc({
	# 				"doctype": "User",
	# 				"first_name": self.beneficiary_name,
	# 				"email": self.email,
	# 				"user_type": "Website User",
	# 				"send_welcome_email": 1,
	# 				"role_profile_name":"Beneficiary"
	# 				}).insert(ignore_permissions = True)
	# 			frappe.get_doc("User", self.email).add_roles("Beneficiary")
	# 			pwd=random_string(10)
	# 			_update_password(user=self.email, pwd=pwd, logout_all_sessions=0)
	# 			# user.new_password="1234"
	# 			self.default_password=pwd
	# 			self.is_user=1
	# 	if self.is_user==0:
	# 		frappe.throw("Beneficiary doesn't add to Users list",raise_exception)

	# 	if self.is_user==1 and self.has_contact==1:
		
	# 			userpermission = frappe.get_doc({
	# 				"doctype": "User Permission",
	# 				"user": user.email,
	# 				"for_value": self.beneficiary_name,
	# 				"allow": "Beneficiary",
	# 				"is_default":1,
	# 				"apply_to_all_doctypes":0,
	# 				"applicable_for":"Beneficiary"
					
	# 				}).insert()
	# 			self.has_user_permission=1
	# 	if self.has_user_permission==0:
	# 		frappe.throw("Beneficiary doesn't add to User Permission list",raise_exception)
		# if self.is_user ==1 and self.has_contact==1 and self.has_user_permission==1:

# def get_item_details(args=None):
# 	item = frappe.db.sql("""select i.name, id.income_account, id.default_warehouse, id.cost_center, id.project, id.project_activities 
# 			from `tabItem` i LEFT JOIN `tabItem Default` id ON i.name=id.parent and id.company=%s
# 			where i.name=%s
# 				and i.disabled=0
# 				and (i.end_of_life is null or i.end_of_life='0000-00-00' or i.end_of_life > %s)""",
# 			(args.get('company'), args.get('item_code'), nowdate()), as_dict = True)
# 	if not item:
# 			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

# 	return item[0]
		
# @frappe.whitelist()
# def get_conversion_factor(item_code, uom):
# 	return frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom': uom}, 'conversion_factor')


# from erpnext.stock.get_item_details import get_valuation_rate
# from erpnext.accounts.utils import get_company_default

# @frappe.whitelist()
# def get_item_detail(item_code, is_fixed_asset, asset_category, company, type):
# 	item_dict = {}
# 	item_details = get_item_details({'item_code': item_code, 'company': company})
# 	item_dict['warehouse'] = item_details.get('default_warehouse')
# 	item_dict['income_account'] = (item_details.get("income_account") or get_item_group_defaults(item_code, company).get("income_account") or 
# 			get_company_default(company, "default_income_account") or frappe.get_cached_value('Company',  company, 
# 			"default_income_account"))
# 	# if type == 'Asset':
# 	# 	item_dict['asset_location'] = frappe.db.get_value('Asset', {'item_code': item_code}, 'location')
# 	item_dict['cost_center'] = item_details.get('cost_center')
# 	item_dict['project'] = item_details.get('project')
# 	item_dict['project_activities'] = item_details.get('project_activities')
# 	val = get_valuation_rate(item_code, company, item_dict['warehouse'])
# 	item_dict['valuation_rate'] = val['valuation_rate'] if val and 'valuation_rate' in val else 1

# 	warehouse_account = get_warehouse_account_map(company)
# 	stock_item = frappe.db.sql("""select name from `tabItem` where name in (%s) and is_stock_item=1""" , [item_code])

# 	# if stock_item and is_fixed_asset == '0':
# 	# 	item_dict['expense_account'] = warehouse_account[item_dict['warehouse']]["account"]
# 	# elif is_fixed_asset == '1' and asset_category:
# 	# 	asset_account = get_asset_category_account(asset_category=asset_category, \
# 	# 		fieldname='fixed_asset_account', company=company)
# 	# 	item_dict['expense_account'] = asset_account

# 	return item_dict



