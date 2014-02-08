Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between `$..$` for inline math and `$$..$$` for displayed math. It also allows for 
writing equations in by using `\begin{equation}`...`\end{equation}`.

Installation
------------

To enable, ensure that `latex.py` is put somewhere that is accessible.
Then use as follows by adding the following to your settings.py:

    PLUGINS = ["latex"]

Be careful: Not loading the plugin is easy to do, and difficult to detect. To
make life easier, find where pelican is installed, and then copy the plugin
there. An easy way to find where pelican is installed is to verbose list the
available themes by typing `pelican-themes -l -v`. 

Once the pelican folder is found, copy `latex.py` to the `plugins` folder. Then 
add to settings.py like this:

    PLUGINS = ["pelican.plugins.latex"]

Now all that is left to do is to embed the following to your template file 
between the `<head>` parameters (for the NotMyIdea template, this file is base.html)

    {% if article and article.latex %}
        {{ article.latex }}
    {% endif %}
    {% if page and page.latex %}
        {{ page.latex }}
    {% endif %}

### Typogrify
Typogrify will now play nicely with Latex (i.e. typogrify can be enabled
and Latex will be rendered correctly). In order for this to happen, 
version 2.07 (or above) of typogrify is required.

Usage
-----
There are two ways to set the plugin:

 1. Old historical way (which still works for backward compatibility reasons)
 2. New way, which will give a template designer more control over the look 
and feel of the Math

### Old historical way
By default, Latex will be embedded in every article.
If however you want latex only for selected articles, 
then in settings.py, add

    LATEX = 'article'

And in each article, add the metadata key `latex:`. For example, with the above
settings, creating an article that I want to render latex math, I would just 
include 'Latex' as part of the metadata without any value:

    Date: 1 sep 2012
    Status: draft
    Latex:

### New way
Options can be set both in settings.py, and also as
value in the metadata. Metadata values will override
settings.py, but only apply on a per article basis.
Metadata cannot override everything put in settings.py,
only style data (like color)

Options is a dictionary, with the following keys:

 * embed: [article|all] - defaulted to all
  * controls where the latex is embedded. Setting embed to article
    means latex will be in articles that request it. An article
    is considered to request latex if there is a metadata key 
    called 'Latex'. This also applies to static pages. A value of ``all``
    will embed latex in the whole document.
 * wrap: [True|False] - defaulted to False
  * If set to true, then all latex is guaranteed to be wrapped 
    in the tags <mathjax>...</mathjax>. This could be useful for
    template design or custom styling. Note: even if wrap is set to
    false, latex will still be wrapped in <mathjax>...</mathjax> if
    using Typogrify.
 * color: [css color] - defaulted to black
  * The color that the latex math is rendered in.

For example, in settings.py, I could so this:

    LATEX = {'embed':'article','color':'blue','wrap':True}

In every article, I could also embed a dictionary in the latex
metadata

    Latex: {'color':'yellow'}

Latex Examples
--------------
###Inline
Latex between `$`..`$`, for example, `$`x^2`$`, will be rendered inline 
with respect to the current html block.

###Displayed Math
Latex between `$$`..`$$`, for example, `$$`x^2`$$`, will be rendered centered in a 
new paragraph.

###Equations
Latex between `\begin` and `\end`, for example, `begin{equation}` x^2 `\end{equation}`, 
will be rendered centered in a new paragraph with a right justified equation number 
at the top of the paragraph. This equation number can be referenced in the document. 
To do this, use a `label` inside of the equation format and then refer to that label 
using `ref`. For example: `begin{equation}` `\label{eq}` X^2 `\end{equation}`. Now 
refer to that equation number by `$`\ref{eq}`$`.
 
Template And Article Examples
-----------------------------
To see an example of this plugin in action, look at 
[this article](http://doctrina.org/How-RSA-Works-With-Examples.html). To see how 
this plugin works with a template, look at 
[this template](https://github.com/barrysteyn/pelican_theme-personal_blog).
