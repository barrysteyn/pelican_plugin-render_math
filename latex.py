# -*- coding: utf-8 -*-
"""
Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.

Typogrify Compatibility
-----------------------
This plugin now plays nicely with typogrify, but it requires
typogrify version 2.07 or above
"""

from pelican import signals
from pelican import contents
import re

# Reference about dynamic loading of MathJax can be found at http://docs.mathjax.org/en/latest/dynamic.html
# The https cdn address can be found at http://www.mathjax.org/resources/faqs/#problem-https
latexScript = """
    <script type= "text/javascript">
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.src = 'https:' == document.location.protocol ? 'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js' : 'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'; 
        s[(window.opera ? "innerHTML" : "text")] =
            "MathJax.Hub.Config({" + 
            "    config: ['MMLorHTML.js']," + 
            "    jax: ['input/TeX','input/MathML','output/HTML-CSS','output/NativeMML']," +
            "    TeX: { extensions: ['AMSmath.js','AMSsymbols.js','noErrors.js','noUndefined.js'], equationNumbers: { autoNumber: 'AMS' } }," + 
            "    extensions: ['tex2jax.js','mml2jax.js','MathMenu.js','MathZoom.js']," +
            "    tex2jax: { " +
            "        inlineMath: [ [\'$\',\'$\'] ], " +
            "        displayMath: [ [\'$$\',\'$$\'] ]," +
            "        processEscapes: true "+
            "    }, " +
            "    'HTML-CSS': { " +
            "        styles: { '.MathJax .mo, .MathJax .mi': {color: 'black ! important'}} " +
            "    } " +
            "}); ";
        (document.body || document.getElementsByTagName('head')[0]).appendChild(s);
    </script>
"""

def addLatex(gen, metadata):
    """
        The registered handler for the latex plugin. It will add 
        the latex script to the article metadata
    """
    try:
        if gen.settings['LATEX'] == 'article' and 'latex' in metadata.keys():
            metadata['latex'] = latexScript
    except KeyError:
        metadata['latex'] = latexScript

def applyTypogrify(instance):
    """
        Will wrap <mathjax> tags around latex if typogrify option
        has been enabled, and then apply typogrfiy filters
        with a setting to ignore <mathjax> tags (need version 
        2.07 of typogrify or above for this)
    """

    if not instance._content:
        return

    try:
        applyTypogrify.latexRe
    except AttributeError:
        # Store regex variable as a function variable so we don't have to recompile all the time
        applyTypogrify.latexRe = re.compile(r'(\$\$|\$).*?\1|\\begin\{(.+?)\}.*?\\end\{\2\}', re.DOTALL | re.IGNORECASE)

    def mathTagWrap(match):
        return '<mathjax>'+match.group(0)+'</mathjax>'

    instance._content, numSubs = applyTypogrify.latexRe.subn(mathTagWrap, instance._content) 

    ignoreTags = ['mathjax'] if numSubs > 0 else None
    from typogrify.filters import typogrify
    instance._content = typogrify(instance._content, ignoreTags)
    instance.metadata['title'] = typogrify(instance.metadata['title'])

def pelicanInit(pelicanObj):
    """
        Determines if Typogrify setting is true. If
        set to true, then set it to false and register
        the applyTypogrfiy plugin which will handle 
        typogrfiy without disturbing latex
    """

    try:
        if pelicanObj.settings['TYPOGRIFY'] == True:
            pelicanObj.settings['TYPOGRIFY'] = False
            signals.content_object_init.connect(applyTypogrify)
    except KeyError:
        pass

def register():
    """
        Plugin registration
    """
    signals.initialized.connect(pelicanInit) # used for typogrify functionality
    signals.article_generator_context.connect(addLatex)
    signals.page_generator_context.connect(addLatex)
