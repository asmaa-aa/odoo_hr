# -*- coding:utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError

import logging as log

from datetime import datetime
from dateutil.relativedelta import relativedelta

global_datas = {}
class elo_hr_contract_report(models.TransientModel):
    """
    :class:'hr_contract_report' Class
    =================================
    This class populate and display the Wizard and generate the Contract's Reports
    """

    _name = 'elo.hr.contract.report'
    _description ='Rapport de contrat'

    """
    Parameters
    ----------
    :param employee_id: Selected contract ID
    :type employee_id: Many2one(str).
    :param name_report: Name of the template report used to generat the report
    :type name_report: Selection(str).
    :param date_from: Start work date
    :type date_from: date.
    :param date_to: End work date
    :type date_to: date.
    """

    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    structure_type_id = fields.Many2one('hr.payroll.structure.type', string='Structure', readonly=True)

    contract_ids = fields.Many2many('hr.contract', string='Contrat')

    name_report = fields.Selection([('attestation', 'Attestation de Travail'),
                                    ('certificate', 'Certificat de Travail')],
                                   default='attestation', required=True, string="Nom de rapport")
    
    sequence = fields.Char("Référence")
    structure = fields.Selection([
        ('employee', 'Employé'),
        ('consultant', 'Consultant')
    ], string='Structure', required=True, default='employee')


    @api.model
    def get_datas(self):
        global global_datas
        return global_datas
    
    @api.onchange('structure')
    def _onchange_structure(self):
        """Met à jour les contrats en fonction de la structure choisie"""
        if self.structure == 'employee':
            # Récupérer les contrats salariés
            contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),('structure_type_id.name', '=', 'Employee') ])   
           
        elif self.structure == 'consultant' :

            # Récupérer les contrats consultants
            contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),('structure_type_id.name', '=', 'Consultant') ])   

        else:
            contracts = self.env['hr.contract']
        
        self.contract_ids = contracts


    def elo_wizard_view_report(self, created_id):
        """this function create and display the wizard

        :returns: this returns the wizard's view information
        :rtype: (string, string, [],[], string, string, string, string, string)

        """
        view = self.env.ref('eloapps_hr_dz.hr_contract_report_view')
        log.warning("----- view --->{} ".format(view.id))
        return {
            'name': _("Attestation/Certificat"),
            'view_mode': 'form',
            'view_id': view.id,
            'view_type': 'form',
            'res_model': 'elo.hr.contract.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': created_id,
        }

    def elo_print_report(self, context=None):
        """this function creates a Contract Report and generate it as PDF

        :returns: this returns an 'action.report'
        :rtype: action

        """
        
        global global_datas
        global_datas.update({
        'employee_id': self.employee_id.id,
        'contract_ids': self.employee_id.contract_ids.ids,
        
        })

        name_report = self.name_report
        if name_report == 'certificate':
            report_name = 'eloapps_hr_dz.hr_employee_certificate'
            
        elif name_report == 'attestation':
            report_name = 'eloapps_hr_dz.hr_employee_attestation'
            
      

        global_datas.update({
            'sequence': self.sequence,
                        })


        return self.env.ref(report_name).report_action(self)



    
