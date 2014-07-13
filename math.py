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

import sys
import os
import re
import mathjax_markdown_extension

from pelican import signals
from pelican import contents


# Global Variables
_TYPOGRIFY = None  # if Typogrify is enabled, this is set to the typogrify.filter function
_WRAP_LATEX = None  # the tag to wrap LaTeX math in (needed to play nicely with Typogrify or for template designers)
_MATH_REGEX = re.compile(r'(\$\$|\$|\\begin\{(.+?)\}|<(math)(?:\s.*?)?>).*?(\1|\\end\{\2\}|</\3>)', re.DOTALL | re.IGNORECASE)  # used to detect math
_MATH_SUMMARY_REGEX = None  # used to match math in summary
_MATH_INCOMPLETE_TAG_REGEX = None  # used to match math that has been cut off in summary
_MATHJAX_SETTINGS = {}  # settings that can be specified by the user, used to control mathjax script settings
with open (os.path.dirname(os.path.realpath(__file__))+'/mathjax_script.txt', 'r') as mathjax_script:  # Read the mathjax javascript from file
    _MATHJAX_SCRIPT=mathjax_script.read()

def process_settings(settings):
    """Sets user specified MathJax settings (see README for more details)"""

    global _MATHJAX_SETTINGS

    # NOTE TO FUTURE DEVELOPERS: Look at the README and what is happening in
    # this function if any additional changes to the mathjax settings need to
    # be incorporated. Also, please inline comment what the variables
    # will be used for

    # Default settings
    _MATHJAX_SETTINGS['align'] = 'center'  # controls alignment of of displayed equations (values can be: left, right, center)
    _MATHJAX_SETTINGS['indent'] = '0em'  # if above is not set to 'center', then this setting acts as an indent
    _MATHJAX_SETTINGS['show_menu'] = 'true'  # controls whether to attach mathjax contextual menu
    _MATHJAX_SETTINGS['process_escapes'] = 'true'  # controls whether escapes are processed
    _MATHJAX_SETTINGS['latex_preview'] = 'TeX'  # controls what user sees while waiting for LaTex to render
    _MATHJAX_SETTINGS['color'] = 'black'  # controls color math is rendered in

    # Source for MathJax: default (below) is to automatically determine what protocol to use
    _MATHJAX_SETTINGS['source'] = """'https:' == document.location.protocol
                ? 'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
                : 'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'"""

    # This next setting controls whether the mathjax script should be automatically
    # inserted into the content. The mathjax script will not be inserted into
    # the content if no math is detected. For summaries that are present in the
    # index listings, mathjax script will also be automatically inserted.
    # Setting this value to false means the template must be altered if this
    # plugin is to work, and so it is only recommended for the template
    # designer who wants maximum control.
    _MATHJAX_SETTINGS['auto_insert'] = True  # controls whether mathjax script is automatically inserted into the content

    if not isinstance(settings, dict):
        return

    # The following mathjax settings can be set via the settings dictionary
    # Iterate over dictionary in a way that is compatible with both version 2
    # and 3 of python
    for key, value in ((key, settings[key]) for key in settings):
        if key == 'auto_insert' and isinstance(value, bool):
            _MATHJAX_SETTINGS[key] = value

        if key == 'align' and isinstance(value, str):
            if value == 'left' or value == 'right' or value == 'center':
                _MATHJAX_SETTINGS[key] = value
            else:
                _MATHJAX_SETTINGS[key] = 'center'

        if key == 'indent':
            _MATHJAX_SETTINGS[key] = value

        if key == 'show_menu' and isinstance(value, bool):
            _MATHJAX_SETTINGS[key] = 'true' if value else 'false'

        if key == 'process_escapes' and isinstance(value, bool):
            _MATHJAX_SETTINGS[key] = 'true' if value else 'false'

        if key == 'latex_preview' and isinstance(value, str):
            _MATHJAX_SETTINGS[key] = value

        if key == 'color' and isinstance(value, str):
            _MATHJAX_SETTINGS[key] = value

        if key == 'ssl' and isinstance(value, str):
            if value == 'off':
                _MATHJAX_SETTINGS['source'] = "'http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'"

            if value == 'force':
                _MATHJAX_SETTINGS['source'] = "'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'"


def pelican_init(pelicanobj):
    """Intialializes certain global variables and sets typogogrify setting to
    False should it be set to True.
    """

    global _TYPOGRIFY
    global _WRAP_LATEX
    global _MATH_SUMMARY_REGEX
    global _MATH_INCOMPLETE_TAG_REGEX

    try:
        settings = pelicanobj.settings['MATH']
    except:
        settings = None

    process_settings(settings)

    # Allows MathJax script to be accessed from template should it be needed
    #pelicanobj.settings['MATHJAXSCRIPT'] = _MATHJAX_SCRIPT.format(**_MATHJAX_SETTINGS)

    # Add the new Markdown extension for mathjax to the current markdown extensions
    try:
        pelicanobj.settings['MD_EXTENSIONS'].append(u'render_math.mathjax_markdown_extension')
    except:
        pass

    # If Typogrify set to True, then we need to handle it manually so it does
    # not conflict with LaTeX
    try:
        if pelicanobj.settings['TYPOGRIFY'] is True:
            pelicanobj.settings['TYPOGRIFY'] = False
            try:
                from typogrify.filters import typogrify

                # Determine if this is the correct version of Typogrify to use
                import inspect
                typogrify_args = inspect.getargspec(typogrify).args
                if len(typogrify_args) < 2 or 'ignore_tags' not in typogrify_args:
                    raise TypeError('Incorrect version of Typogrify')

                # At this point, we are happy to use Typogrify, meaning
                # it is installed and it is a recent enough version
                # that can be used to ignore all math
                _TYPOGRIFY = typogrify
                _WRAP_LATEX = 'mathjax' # default to wrap mathjax content inside of
            except ImportError:
                print("\nTypogrify is not installed, so it is being ignored.\nIf you want to use it, please install via: pip install typogrify\n")
            except TypeError:
                print("\nA more recent version of Typogrify is needed for the render_math module.\nPlease upgrade Typogrify to the latest version (anything above version 2.04 is okay).\nTypogrify will be turned off due to this reason.\n")
    except KeyError:
        pass

    # Set _WRAP_LATEX to the settings tag if defined. The idea behind this is
    # to give template designers control over how math would be rendered
    try:
        if pelicanobj.settings['MATH']['wrap_latex']:
            _WRAP_LATEX = pelicanobj.settings['MATH']['wrap_latex']
    except (KeyError, TypeError):
        pass

    # regular expressions that depend on _WRAP_LATEX are set here
    tag_start= r'<%s>' % _WRAP_LATEX if not _WRAP_LATEX is None else ''
    tag_end = r'</%s>' % _WRAP_LATEX if not _WRAP_LATEX is None else ''
    math_summary_regex = r'((\$\$|\$|\\begin\{(.+?)\}|<(math)(?:\s.*?)?>).+?)(\2|\\end\{\3\}|</\4>|\s?\.\.\.)(%s|</\4>)?' % tag_end

    # NOTE: The logic in _get_summary will handle <math> correctly because it
    # is perceived as an html tag. Therefore we are only interested in handling
    # non mml (i.e. LaTex)
    incomplete_end_latex_tag = r'(.*)(%s)(\\\S*?|\$)\s*?(\s?\.\.\.)(%s)?$' % (tag_start, tag_end)

    _MATH_SUMMARY_REGEX = re.compile(math_summary_regex, re.DOTALL | re.IGNORECASE)
    _MATH_INCOMPLETE_TAG_REGEX = re.compile(incomplete_end_latex_tag, re.DOTALL | re.IGNORECASE)


def register():
    """Plugin registration"""
    signals.initialized.connect(pelican_init)
    #signals.content_object_init.connect(process_content)
