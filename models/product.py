# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _record_negation(self, product_qty):
        """Record a negation for product"""

        self.ensure_one()

        ProductRejected = self.env['product.rejected']
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        import logging
        _logger = logging.getLogger(__name__)
        _logger.debug('DEBUG PRODUCT REJECTED USER %s', self.env.user)
        if self.env.user:

            limit_hours = \
                self.env.user.company_id.product_rejected_limit_hours
            if limit_hours > 0:

                last_product_negation = ProductRejected.sudo().search([
                    ('product_id', '=', self.id),
                    ('partner_id', '=', self.env.user.partner_id.id),
                    ('company_id', '=', self.env.user.company_id.id),
                    ], order='date')

                if last_product_negation:

                    last_product_negation_date = \
                        last_product_negation[-1].date
                    last_product_negation_datetime = \
                        datetime.strptime(
                            last_product_negation_date,
                            '%Y-%m-%d %H:%M:%S')
                    now = datetime.now()
                    diff = now - last_product_negation_datetime
                    hours_diff = (diff.seconds / 60.0) / 60

                    if hours_diff > limit_hours:
                        ProductRejected.sudo().create({
                            'product_tmpl_id': self.product_tmpl_id.id,
                            'product_id': self.id,
                            'partner_id': self.env.user.partner_id.id,
                            'qty': product_qty,
                            'date': date_now,
                            'company_id': self.env.user.company_id.id,
                            })

                else:

                    ProductRejected.sudo().create({
                        'product_tmpl_id': self.product_tmpl_id.id,
                        'product_id': self.id,
                        'partner_id': self.env.user.partner_id.id,
                        'qty': product_qty,
                        'date': date_now,
                        'company_id': self.env.user.company_id.id,
                        })

            else:

                ProductRejected.sudo().create({
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'product_id': self.id,
                    'partner_id': self.env.user.partner_id.id,
                    'qty': product_qty,
                    'date': date_now,
                    'company_id': self.env.user.company_id.id,
                    })

        else:

            ProductRejected.sudo().create({
                'product_tmpl_id': self.product_tmpl_id.id,
                'product_id': self.id,
                'qty': product_qty,
                'date': date_now,
                })

    @api.multi
    def check_product_not_available(self, product_qty):

        import logging
        _logger = logging.getLogger(__name__)
        _logger.debug('DEBUG PRODUCT REJECTED USER %s', self.env.user)

        self.ensure_one()

        if self.type == 'product':
            if product_qty > (self.sudo().qty_available -
                              self.sudo().outgoing_qty):

                self._record_negation(product_qty)

        return super(ProductProduct, self).check_product_not_available(
            product_qty)
