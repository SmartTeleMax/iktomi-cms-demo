# -*- coding: utf-8 -*-

import os, logging
from babel.messages.frontend import parse_mapping
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir, DEFAULT_KEYWORDS, \
                                   DEFAULT_MAPPING
from babel.messages.pofile import read_po, write_po
from babel import Locale
from iktomi.cli.base import Cli

logger = logging.getLogger(__name__)


KEYWORDS = dict(DEFAULT_KEYWORDS,
                M_=(1,2))


class I18nCommands(Cli):

    def __init__(self, input_dirs, output_dir, languages, mapping_file=None,
                 reference_dir=None, keywords=KEYWORDS,
                 template_filter=None):
        '''
        input_dirs      — list of directories to scan or dictionary mapping
                          category to list of directories
        output_dir      — root directory for messages catalogue
        languages       — list of languages or dictionary mapping category to
                          list of  languages
        mapping_file    — path to mapping.ini config file
        reference_dir   — reference point directory to calculate relative
                          paths in location comments, usually project root (by
                          default absolute paths are used)
        keywords        — a dictionary mapping keywords (i.e. names of
                          functions that should be recognized as translation
                          functions) to tuples that specify which of their
                          arguments contain localizable strings
        template_filter — predicate function accepting catalog and message
                          arguments and returning if message should be included
                          into catalog
        '''
        if not isinstance(input_dirs, dict):
            input_dirs = {'messages': input_dirs}
        self.input_dirs = input_dirs
        self.output_dir = output_dir
        if not isinstance(languages, dict):
            languages = {'messages': languages}
        self.languages = languages
        if mapping_file is None:
            self.method_map = DEFAULT_MAPPING
            self.options_map = {}
        else:
            with open(mapping_file, 'U') as fp:
                self.method_map, self.options_map = parse_mapping(fp)
        self.reference_dir = reference_dir
        self.keywords = keywords
        self.template_filter = template_filter

    def command_extract(self):

        def callback(filename, method, options):
            filepath = os.path.normpath(os.path.join(dirname, filename))
            optstr = ''
            if options:
                optstr = ' (%s)' % ', '.join(['%s="%s"' % (k, v) for
                                              k, v in options.items()])
            logger.info('Extracting messages from %s%s', filepath, optstr)

        for category, input_dirs in self.input_dirs.items():
            logger.info('Processing category "%s"', category)
            if isinstance(input_dirs, basestring):
                input_dirs = [input_dirs]
            catalog = Catalog()
            for dirname in input_dirs:
                extracted = extract_from_dir(dirname, self.method_map,
                                             self.options_map,
                                             keywords=self.keywords,
                                             callback=callback)
                for filename, lineno, message, comments, context in extracted:
                    path = os.path.normpath(os.path.join(dirname, filename))
                    if self.reference_dir:
                        path = os.path.relpath(path, self.reference_dir)
                    catalog.add(message, None, [(path, lineno)],
                                auto_comments=comments, context=context)
            out_fn = os.path.join(self.output_dir, category+'.pot')
            logger.info('Writing PO template file to %s', out_fn)
            with open(out_fn, 'w') as out_fp:
                write_po(out_fp, catalog, omit_header=True)

    def _filter_template(self, catalog, template):
        '''Remove messages we don't what to see in catalog from template
        (in-place)'''
        if self.template_filter is None:
            return
        for key, message in template._messages.items():
            if key in catalog._messages:
                # We already have translation, so keep it anyway
                continue
            if not self.template_filter(catalog, message):
                del template._messages[key]

    def command_merge(self):
        for category in self.input_dirs.keys():
            logger.info('Processing category "%s"', category)
            pot_fn = os.path.join(self.output_dir, category+'.pot')
            if not os.path.exists(pot_fn):
                logger.warning("PO template file %s doesn't exist", pot_fn)
                continue
            try:
                languages = self.languages[category]
            except KeyError:
                logger.warning('No languages for category "%s"', category)
                continue
            if isinstance(languages, basestring):
                languages = [languages]
            for language in languages:
                with open(pot_fn, 'U') as pot_fp:
                    template = read_po(pot_fp, locale=language)
                po_fn = os.path.join(self.output_dir, language, category+'.po')
                if os.path.exists(po_fn):
                    logger.info('Merging template to PO file %s', po_fn)
                    with open(po_fn, 'U') as po_fp:
                        catalog = read_po(po_fp, locale=language)
                    self._filter_template(catalog, template)
                    catalog.update(template)
                else:
                    logger.info('Creating new PO file %s', po_fn)
                    catalog = Catalog()
                    catalog.locale = Locale.parse(language)
                    catalog.fuzzy = False
                    self._filter_template(catalog, template)
                out_fn = po_fn+'.new'
                with open(out_fn, 'wb') as out_fp:
                    write_po(out_fp, catalog, omit_header=True)
                os.rename(out_fn, po_fn)
