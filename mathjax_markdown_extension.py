# -*- coding: utf-8 -*-
"""
Math Render Plugin for Pelican
==============================
This plugin allows your site to render Math. It supports both LaTeX and MathML
using the MathJax JavaScript engine.

Typogrify Compatibility
-----------------------
This plugin now plays nicely with Typogrify, but it requires
Typogrify version 2.04 or above.

User Settings
-------------
Users are also able to pass a dictionary of settings in the settings file which
will control how the MathJax library renders things. This could be very useful
for template builders that want to adjust the look and feel of the math.
See README for more details.
"""

import os
import markdown

from markdown.util import etree

_MATH_REGEX = r'(?<!\\)(\$\$?|\\begin\{(.+?)\}|<(math)(?:\s.*?)?>)(.+?)(\2|\\end\{\3\}|</\4>)' # used to detect math
with open (os.path.dirname(os.path.realpath(__file__))+'/mathjax_script.txt', 'r') as mathjax_script:  # Read the mathjax javascript from file
    _MATHJAX_SCRIPT=mathjax_script.read()

class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, _MATH_REGEX)

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(5) + m.group(6))
        return node

class MathJaxTreeProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, root):
        mathjax_script = etree.Element('div')
        script = etree.SubElement(mathjax_script, 'script')
        script.set('type','text/javascript')
        script.text = _MATHJAX_SCRIPT
        root.append(mathjax_script)

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Must come before any markdown is processed, specially escapes
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '_begin')

        md.treeprocessors.add('mathjax', MathJaxTreeProcessor(self), '_begin')

def makeExtension(configs=None):
    return MathJaxExtension(configs)
