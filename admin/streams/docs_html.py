# -*- coding: utf-8 -*-
from admin.streams.common import convs, widgets


body_wysihtml5 = widgets.WysiHtml5(
        stylesheets=widgets.WysiHtml5.stylesheets + (
                        '/static/css/wysihtml5-blocks.css', ),
        classname="long",
    ).add_buttons([
        ('advanced', ['createLinkAdvanced', 'doclink'])
    ]).remove_buttons('createLink')


allowed_elements = ['abbr', 'iktomi_doclink', 'iktomi_photo',
                    'iktomi_photoset']

body_conv = convs.ExpandableHtml(
                        required=True,
                        add_allowed_elements=allowed_elements,
                        add_allowed_attributes=['data-align', 'item_id'],
                        add_allowed_protocols=['model'],
                        )
