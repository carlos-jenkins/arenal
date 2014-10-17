# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Directive to generate graphs using Graphviz.

Options:
  - path: prefix without extension.
            e.g. "images/login" will generate "images/login.dot" and
                 "images/login.(png/svg)".

          Files will usualy be OVERWRITTEN. But if no content is specified
          and .dot file exists, render will be generated from this file.
"""

from os.path import join, abspath, dirname
from subprocess import call
from traceback import format_exc
from shlex import split as shsplit
from distutils.dir_util import mkpath

from docutils import nodes
from docutils.parsers.rst.directives.images import Image


class Graph(Image):

    dot_out_dir = 'images'

    dot_emb_ext = '.png'
    dot_out_ext = '.png'
    dot_cmd_args = '-Tpng'

    required_arguments = 0
    optional_arguments = 1
    option_spec = Image.option_spec.copy()
    has_content = True

    def run(self):

        # Check if file insertion is enabled
        if not self.state.document.settings.file_insertion_enabled:
            msg = (
                'File and URL access deactivated. '
                'Ignoring directive "{}".'.format(self.name)
            )
            warning = nodes.warning(
                '', self.state_machine.reporter.warning(
                    '', nodes.literal_block('', msg),
                    line=self.lineno
                )
            )
            return [warning]

        # Define dot file name
        if len(self.arguments) > 0:
            fname = self.arguments[0]
        else:
            fname = '{:06d}'.format(self.lineno)
        fname = join(self.dot_out_dir, fname)

        # Create images output folder
        mkpath(abspath(dirname(fname)))

        # Write plantuml content
        dot_file = fname + '.dot'
        if self.content:
            with open(dot_file, 'wb') as fd:

                try:
                    fd.write(
                        self.state_machine.document.settings.dot_hdr
                    )
                    fd.write('\n')
                except AttributeError:
                    pass
                fd.write('\n'.join(self.content))

        # Execute Graphviz call
        image_file = fname + self.dot_out_ext
        dot_cmd = 'dot'
        try:
            dot_cmd = self.state_machine.document.settings.dot_cmd
        except AttributeError:
            pass

        try:
            code = call(shsplit(
                '{} {} -o "{}" "{}"'.format(
                    dot_cmd, self.dot_cmd_args, image_file, dot_file
                )
            ))
            if code != 0:
                raise Exception('dot call returned {}.'.format(code))
        except:
            msg = format_exc()
            error = nodes.error(
                '', self.state_machine.reporter.error(
                    '', nodes.literal_block('', msg),
                    line=self.lineno
                )
            )
            return [error]

        # Default to align center
        if not 'align' in self.options:
            self.options['align'] = 'center'

        # Run Image directive
        self.arguments = [fname + self.dot_emb_ext]
        return Image.run(self)

    @classmethod
    def configure(cls, format, raster=False, **kwargs):
        """
        Configure directive to behave in different ways depending on the format
        and specific options.
        """

        if raster:
            cls.dot_emb_ext = '.png'
            cls.dot_out_ext = '.png'
            cls.dot_cmd_args = '-Tpng'
            return

        cls.dot_emb_ext = '.svg'
        cls.dot_out_ext = '.svg'
        cls.dot_cmd_args = '-Tsvg'

        if format == 'latex':
            cls.dot_emb_ext = '.pdf'

__all__ = ['Graph']
