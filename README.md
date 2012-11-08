Latex Plugin For Pelican
========================

This plugin allows you to write mathematical equations in your articles using Latex.
It uses the MathJax Latex JavaScript library to render latex that is embedded in
between $..$. It also allows for writing equations in by using \begin{equation}...
\end{equation}.

Settings
--------
To enable, ensure that the plugin is installed somewhere that is accessible.
Then use as follows by adding:

    PLUGINS = ["latex"]

to your settings.py

Be careful: Not loading the plugin is eas to do, and difficult to detect. To
make life easier, find where pelican is installed, and then copy the plugin
there. Then do this:

    PLUGINS = ["pelican.plugins.latex"]

Usage
-----
Add the following to your template file between the <head> parameters (for
the NotMyIdea template, this file is base.html)

    {% if article and article.latex %}
        {{ article.latex }}
    {% endif %}

Now latex will be embedded in every article. If however you want latex only for
selected articles, then in settings.py, add

    LATEX = 'article'

And in each article, add the metadata key 'latex'. For example, with the above
settings, creating an article called math, I would just include 'latex' as
part of the metadata:

    Date: 1 sep 2012
    Status: draft
    Latex:
