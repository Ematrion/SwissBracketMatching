# LaTeX escape mappings
LATEX_ESCAPE_MAP = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    #'_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\^{}',
    '\\': r'\textbackslash{}'
}

def escape_latex(text):
    """
    Escape special LaTeX characters in text.
    
    Parameters:
    -----------
    text : str
        Text to escape
    
    Returns:
    --------
    str : LaTeX-safe text
    """
    for char, replacement in LATEX_ESCAPE_MAP.items():
        text = text.replace(char, replacement)
    return text