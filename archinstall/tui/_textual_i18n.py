"""Translation markers for Textual's built-in key binding descriptions.

archinstall translates every key binding description at runtime (see
``components.py::_translate_bindings``), including the bindings that Textual
defines internally on its own widgets, screens and app. Those descriptions
(e.g. "Cursor up", "Page Down", "Toggle option") live inside the installed
``textual`` package, so xgettext scanning archinstall's own sources would never
see them and they would stay untranslated in the F1 help panel.

This module marks those descriptions with ``N_()`` so xgettext extracts them
into ``base.pot`` (the standard gettext ``gettext_noop`` pattern). Nothing here
is executed at runtime - it exists purely to be scanned by the locale generator.

Keep this list in sync with the descriptions Textual ships. Regenerate the
candidates with:

    python -c "from textual.app import App; from textual.screen import Screen; \\
        from textual.widgets import (Button, DataTable, Footer, Input, Label, \\
        LoadingIndicator, OptionList, Rule, SelectionList); \\
        seen = {}; \\
        [seen.setdefault(b.description, None) \\
            for c in (App, Screen, Button, DataTable, Footer, Input, Label, \\
                LoadingIndicator, OptionList, Rule, SelectionList) \\
            for k in c.__mro__ for b in k.__dict__.get('BINDINGS', []) \\
            if getattr(b, 'description', None) and not getattr(b, 'system', False)]; \\
        print('\\n'.join(seen))"
"""

from archinstall.lib.translationhandler import N_

# Textual built-in binding descriptions (textual==8.2.8), grouped by widget.

# App / Screen
N_('Quit')
N_('Focus Next')
N_('Focus Previous')

# Button
N_('Press button')

# OptionList
N_('Down')
N_('Up')
N_('First')
N_('Last')
N_('Page Up')
N_('Page Down')
N_('Select')

# SelectionList
N_('Toggle option')

# DataTable
N_('Cursor up')
N_('Cursor down')
N_('Cursor left')
N_('Cursor right')
N_('Page up')
N_('Page down')
N_('Home')
N_('End')
N_('Top')
N_('Bottom')

# Footer (scrolling helpers surfaced in the help panel)
N_('Scroll Up')
N_('Scroll Down')
N_('Scroll Left')
N_('Scroll Right')
N_('Scroll Home')
N_('Scroll End')
N_('Page Left')
N_('Page Right')

# Input
N_('Move cursor left')
N_('Move cursor right or accept the completion suggestion')
N_('Move cursor left a word')
N_('Move cursor right a word')
N_('Move cursor left and select')
N_('Move cursor right and select')
N_('Move cursor left a word and select')
N_('Move cursor right a word and select')
N_('Go to start')
N_('Go to end')
N_('Select line start')
N_('Select line end')
N_('Select all')
N_('Delete character left')
N_('Delete character right')
N_('Delete left to start of word')
N_('Delete right to start of word')
N_('Delete all to the left')
N_('Delete all to the right')
N_('Copy selected text')
N_('Cut selected text')
N_('Paste text from the clipboard')
N_('Submit')
