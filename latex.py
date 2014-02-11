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
    </script>"""

def inRange(t, tupleList):
    """
        Determines if t is within tupleList.
        Does this in efficiently: logN
    """

    ignore = False
    if tupleList == []:
        return False

    for index in range(2):
        lo = 0
        hi = len(tupleList)-1

        # Find first value in array where predicate is True
        # predicate function: tupleList[mid][0] > t[index]
        while (lo < hi):
            mid = lo + (hi-lo+1)/2
            if tupleList[mid][0] > t[index]:
                hi = mid-1
            else:
                lo = mid

        ignore = ignore or (tupleList[lo][0] <= t[index] and tupleList[lo][1] >= t[index])
        if (ignore):
            return True

    return ignore

# Default Values
# Note to future developers: I have given an example with color over here, but
# it should be easy enough to add settings if needed
latexScript.color = 'black' # Note: not set as #000 so as to aide in readbility

def searchForLatex(content, wrapTag=None):
    """
        Wraps latex in user specified tags. This
        is needed for typogrify to play nicely with latex
        but it can also be styled by templated providers
    """
    ignoreList = []
    searchForLatex.latex = False

    def mathTagWrap(match):
        ignore = inRange(match.span(), ignoreList)
        if not searchForLatex.latex and not ignore:
            searchForLatex.latex = True

        return '<'+wrapTag+'>'+match.group(0)+'</'+wrapTag+'>' if not ignore else match.group(0)

    if wrapTag: 
        # Ignore tags that are within <code> and <pre> blocks
        for match in searchForLatex.codepreregex.finditer(content):
            ignoreList.append(match.span())

        return (searchForLatex.regex.sub(mathTagWrap, content), searchForLatex.latex)

    return True if searchForLatex.regex.search(content) else False

searchForLatex.regex = re.compile(r'(\$\$|\$).*?\1|\\begin\{(.+?)\}.*?\\end\{\2\}', re.DOTALL | re.IGNORECASE)
searchForLatex.codepreregex = re.compile(r'<pre>.*?</pre>|<code>.*?</code>', re.DOTALL | re.IGNORECASE)

def processSettings(dictObj):
    """
        Set user specified MathJax settings (see README for more details)
    """
    if type(dictObj).__name__ != 'dict':
        return

    for key, value in ((key, dictObj[key]) for key in dictObj): # iterate that is compatible with both version 2 and 3 of python
        if key == 'color':
            latexScript.color = value
    

def processContent(instance):
    if not instance._content:
        return

    if processContent.wrapTag:
        instance._content, latex = searchForLatex(instance._content, processContent.wrapTag)
    else:
        latex = searchForLatex(instance._content)

    if processContent.typogrify:
        from typogrify.filters import typogrify
        ignoreTags = [processContent.wrapTag] if processContent.wrapTag else None

        instance._content = typogrify(instance._content, ignoreTags)
        instance.metadata['title'] = typogrify(instance.metadata['title'], ignoreTags)

    if latex:
        instance.metadata['latex'] = latexScript()
        instance._content += latexScript() # mathjax script added to the end of article

def pelicanInit(pelicanObj):
    """
        Determines if Typogrify setting is true. If
        set to true, then set it to false and register
        the applyTypogrfiy plugin which will handle 
        typogrfiy without disturbing latex
    """

    try:
        processSettings(pelicanObj.settings['LATEX'])
    except:
        pass

    processContent.typogrify = False
    processContent.wrapTag = None

    # If typogrify set to True, then we need to handle 
    # it manually so it does not conflict with Latex
    try: 
        if pelicanObj.settings['TYPOGRIFY'] == True:
            pelicanObj.settings['TYPOGRIFY'] = False
            processContent.wrapTag = 'mathjax'
            processContent.typogrify = True
    except KeyError:
        pass

    try: # See if latex should be wrapped in tags
        if pelicanObj.settings['LATEX']['wrap']:
            processContent.wrapTag = pelicanObj.settings['LATEX']['wrap']
    except (KeyError, TypeError):
        pass


def register():
    """
        Plugin registration
    """
    signals.initialized.connect(pelicanInit) 
    signals.content_object_init.connect(processContent)
