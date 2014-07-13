# -*- coding: utf-8 -*-
"""
Pelican Mathjax Markdown Extension
==================================
An extension for the Python Markdown module that enables
the Pelican python blog to process mathjax. This extension
gives Pelican the ability to use Mathjax as a "first class
citizen" of the blog
"""

import markdown

from markdown.util import etree
from markdown.util import AtomicString

class PelicanMathJaxPattern(markdown.inlinepatterns.Pattern):
    """Inline Pattern for matching mathjax"""

    def __init__(self, pelican_mathjax_extension):
        super(PelicanMathJaxPattern,self).__init__(pelican_mathjax_extension.mathjax_regex)
        self.math_tag_wrap = pelican_mathjax_extension.getConfig('math_tag_wrap')
        self.pelican_mathjax_extension = pelican_mathjax_extension

    def handleMatch(self, m):
        node = markdown.util.etree.Element(self.math_tag_wrap)
        node.text = markdown.util.AtomicString(m.group(2) + m.group(5) + m.group(6))

        # If mathjax was successfully matched, then JavaScript needs to be added
        # for rendering. The boolean below indicates this
        self.pelican_mathjax_extension.mathjax_needed = True
        return node

class PelicanMathJaxTreeProcessor(markdown.treeprocessors.Treeprocessor):
    """Tree Processor for adding Mathjax JavaScript to the blog"""

    def __init__(self, pelican_mathjax_extension):
        self.pelican_mathjax_extension = pelican_mathjax_extension

    def run(self, root):

        # If no mathjax was present, then exit
        if (not self.pelican_mathjax_extension.mathjax_needed):
            return

        # Add the mathjax script to the html document
        mathjax_script = etree.Element('div')
        script = etree.SubElement(mathjax_script, 'script')
        script.set('type','text/javascript')
        script.text = AtomicString(self.pelican_mathjax_extension.getConfig('mathjax_script'))
        root.append(mathjax_script)

        # Reset the boolean switch to false so that script is only added
        # to other pages if needed
        self.pelican_mathjax_extension.mathjax_needed = False

class PelicanMathJaxExtension(markdown.Extension):
    """A markdown extension enabling mathjax processing in Markdown for Pelican"""

    def __init__(self, config):
        super(PelicanMathJaxExtension,self).__init__(config)

        # Regex to detect mathjax. To note that it also classifies LaTeX macros as mathjax
        self.mathjax_regex = r'(?<!\\)(\$\$?|\\begin\{(.+?)\}|<(math)(?:\s.*?)?>)(.+?)(\2|\\end\{\3\}|</\4>)'
        self.mathjax_needed = False

    def extendMarkdown(self, md, md_globals):
        # Process mathjax before escapes are processed since escape processing will
        # intefer with mathjax
        md.inlinePatterns.add('mathjax', PelicanMathJaxPattern(self), '<escape')

        # If necessary, add the JavaScript Mathjax library to the document. This must
        # be last in the ordered dict (hence it is given the position '_end')
        md.treeprocessors.add('mathjax', PelicanMathJaxTreeProcessor(self), '_end')
