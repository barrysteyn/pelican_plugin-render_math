# -*- coding: utf-8 -*-
"""
Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.
"""

from pelican import signals

latexScript = """
    <script src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type= "text/javascript">
       MathJax.Hub.Config({
           config: ["MMLorHTML.js"],
           jax: ["input/TeX","input/MathML","output/HTML-CSS","output/NativeMML"],
           TeX: { extensions: ["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"], equationNumbers: { autoNumber: "AMS" } },
           extensions: ["tex2jax.js","mml2jax.js","MathMenu.js","MathZoom.js"],
           tex2jax: { 
               inlineMath: [ [\'$\',\'$\'] ],
               displayMath: [ [\'$$\',\'$$\'] ],
               processEscapes: true },
           "HTML-CSS": {
               styles: { ".MathJax .mo, .MathJax .mi": {color: "black ! important"}}
           }
       });
    </script>
"""

def addLatex(gen, metadata):
    """
        The registered handler for the latex plugin. It will add 
        the latex script to the article metadata
    """
    if 'LATEX' in gen.settings.keys() and gen.settings['LATEX'] == 'article':
        if 'latex' in metadata.keys():
            metadata['latex'] = latexScript
    else:
        metadata['latex'] = latexScript

def mathTag(instance):
    try:
        mathTag.latexRe
    catch AttributeError:
        mathTag=re.compile(r"")

    def insertMathTag(matchObj):
        return "<math>"+matchObj.group(0)+"</math>"


    if 'TYPOGRIFY' in instance.settings.keys() and instance.settings['TYPOGRIFY'] == True:
        instance._content = re.sub(r'', insertMathTag, instance._content, 0, re.IGNORECASE) 

def register():
    """
        Plugin registration
    """
    signals.article_generator_context.connect(addLatex)
    signals.page_generator_context.connect(addLatex)
    signals.content_object_init.connect(mathTag)
