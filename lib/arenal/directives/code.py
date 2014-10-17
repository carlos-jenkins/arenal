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
Code syntax highlight directive using Pygments.
"""

from pygments.formatters import HtmlFormatter, LatexFormatter

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.util import ClassNotFound


FORMATTERS_MAP = {
    'html' : (HtmlFormatter, 'monokai'),
    'latex': (LatexFormatter, 'default')
}


def nonnegative_int_list(argument):
    """
    Check for a list of nonnegative integer arguments;
    raise ``ValueError`` if not. (Directive option conversion function.)
    """
    tokens = map(int, argument.strip().split(','))
    if any(map(lambda x: x < 0, tokens)):
        raise ValueError('negative value; must be positive or zero')
    return sorted(set(tokens))


class Code(Directive):
    """
    Code syntax highlight directive using Pygments.
    """
    # Configuration options
    code_format = 'html'

    # Directive framework options
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    final_argument_whitespace = True

    option_spec = {
        'linenos': directives.flag,
        'linenostart': directives.nonnegative_int,
        'linenostep': directives.nonnegative_int,
        'lineanchors': directives.flag,
        'hl_lines': nonnegative_int_list,
    }

    def run(self):

        self.assert_has_content()

        # Get lexer (string -> tokens)
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ClassNotFound:
            # No lexer found - use the text one instead of an exception
            lexer = TextLexer()

        # Get formatter (tokens -> target output)
        lineanchors = ''
        if 'lineanchors' in self.options:
            lineanchors = str(self.lineno)

        clss, style = FORMATTERS_MAP[self.code_format]
        formatter = clss(
            style=style,
            # Display line numbers
            linenos='linenos' in self.options,
            # Line start
            linenostart=self.options.get('linenostart', 1),
            # Step to print line number
            linenostep=self.options.get('linenostep', 1),
            # CSS class (HTML only, ignored by LaTeX)
            cssclass='code',
            # Add line anchor (HTML only, ignored by LaTeX)
            lineanchors=lineanchors,
            # Highlight lines (HTML only, ignored by LaTeX)
            hl_lines=self.options.get('hl_lines', []),
        )

        # Highlight code
        parsed = highlight(
            u'\n'.join(self.content),
            lexer,
            formatter
        )

        #print(self.options)

        # Return a raw node with the highlighted code
        return [nodes.raw('', parsed, format=self.code_format)]

    @classmethod
    def configure(cls, format, **kwargs):
        """
        Configure directive to behave in different ways depending on the format
        and specific options.
        """
        cls.code_format = format
