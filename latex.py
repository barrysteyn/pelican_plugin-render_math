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
typogrify version 2.07 or above. 

User Settings
-------------
Users are also able to pass a dictionary of settings, either in the settings file, or
in the metadata (which will overload the settings file). This could be very useful
for template builders that want to adjust look and feel of the math.
See README for more details.
"""

from pelican import signals
from pelican import contents
import re

# Reference about dynamic loading of MathJax can be found at http://docs.mathjax.org/en/latest/dynamic.html
# The https cdn address can be found at http://www.mathjax.org/resources/faqs/#problem-https

def latexScript():

    return """
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
            "        styles: { '.MathJax_Display, .MathJax .mo, .MathJax .mi': {color: '""" + latexScript.color + """ ! important'}} " +
            "    } " +
            "}); ";
        (document.body || document.getElementsByTagName('head')[0]).appendChild(s);
    </script>
"""


# Default Values
# Note to future developers: I have given an example with color over here, but
# it should be easy enough to add settings if needed
latexScript.color = 'black' # Note: not set as #000 so as to aide in readbility

def setMathJaxSettings(dictObj):
    """
        Set user specified MathJax settings (see README for more details)
    """
    embed = 'page'
    if type(dictObj).__name__ == 'str' or type(dictObj).__name__ == 'unicode':
        try:
            import ast
            dictObj = ast.literal_eval(dictObj)
        except:
            pass

    if type(dictObj).__name__ != 'dict':
        return embed

    for key, value in ((key, dictObj[key]) for key in dictObj): # iterate over dictionary that is compatible with both version 2 and 3
        if key == 'color':
            latexScript.color = value
        if key == 'embed':
            embed = value

    return embed


def addLatex(gen, metadata):
    """
        The registered handler for the latex plugin. It will add 
        the latex script to the article metadata, and set the appropriate settings
    """
    try:
        # backward compatiblity: if in settings, Latex = 'article', then only embed in articles that want it
        if type(gen.settings['LATEX']).__name__ == 'str' and gen.settings['LATEX'] == 'article':
            if 'latex' in metadata.keys():
                metadata['latex'] = latexScript() 
        # see if user has specified explicit settings
        else:
            embed = setMathJaxSettings(gen.settings['LATEX'])
            if 'latex' in metadata.keys():
                setMathJaxSettings(metadata['latex']) # settings in metadata can override global settings

            if embed == 'article':
                if 'latex' in metadata.keys():
                    metadata['latex'] = latexScript() # only emebd in an article that requests it to be there
            else:
                metadata['latex'] = latexScript() # embed latex in every page
    except KeyError:
        metadata['latex'] = latexScript() # default functionality: embed latex in every page of the document


def wrap(content):
    """
        Wraps latex in <mathjax>...</mathjax> tags. This
        is needed for typogrify to play nicely with latex
        but it can also be styled by templated providers
    """

    try:
        wrap.latexRe
    except AttributeError:
        # Store regex variable as a function variable so we don't have to recompile all the time
        wrap.latexRe = re.compile(r'(\$\$|\$).*?\1|\\begin\{(.+?)\}.*?\\end\{\2\}', re.DOTALL | re.IGNORECASE)

    def mathTagWrap(match):
        return '<mathjax>'+match.group(0)+'</mathjax>'

    return wrap.latexRe.subn(mathTagWrap, content) 


def wrapMathInTags(instance):
    """
        If typogrify has been set to false, but latex setting
        'wrap' was set to true, then just wrap latex in
        <mathjax>...</mathjax>. Use case would be for template writers
    """
    if not instance._content:
        return

    instance._content = wrap(instance._content)[0]


def applyTypogrify(instance):
    """
        Will wrap <mathjax> tags around latex if typogrify option
        has been enabled, and then apply typogrfiy filters
        with a setting to ignore <mathjax> tags (need version 
        2.07 of typogrify or above for this)
    """

    if not instance._content:
        return

    instance._content, numSubs = wrap(instance._content)
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

    try: # If typogrify set to True, then we need to handle it manually so it does not conflict with Latex
        if pelicanObj.settings['TYPOGRIFY'] == True:
            pelicanObj.settings['TYPOGRIFY'] = False
            signals.content_object_init.connect(applyTypogrify)

            return
    except KeyError:
        pass

    try: # If typogrify is set to false or is not present, then see if latex should be wrapped in tags
        if pelicanObj.settings['LATEX']['wrap'] == True:
            signals.content_object_init.connect(wrapMathInTags)
    except (KeyError, TypeError):
        pass


def register():
    """
        Plugin registration
    """
    signals.initialized.connect(pelicanInit) 
    signals.article_generator_context.connect(addLatex)
    signals.page_generator_context.connect(addLatex)
