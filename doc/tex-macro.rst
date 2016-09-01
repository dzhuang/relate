.. _latex_to_img:

Built-in LaTeX to image macro
-----------------------------

.. currentmodule:: course.latex

Relate provides a built-in
`Jinja <http://jinja.pocoo.org/docs/dev/templates/>`_ macro named
latex which compiles the source code of a a full LaTex document and
returns its Data URI which can be wrapped by <img> tags in :ref:`markup`.
For example, the following creates a center aligned simple LaTex tabular::

    <p align="middle">
    {% call latex(compiler="pdflatex", image_format="png") %}
    \documentclass{article}
    \usepackage[utf8]{inputenc}
    \usepackage[table]{xcolor}
    \setlength{\arrayrulewidth}{1mm}
    \setlength{\tabcolsep}{18pt}
    \renewcommand{\arraystretch}{2.5}
    \newcolumntype{s}{>{\columncolor[HTML]{AAACED}} p{3cm}}
    \arrayrulecolor[HTML]{DB5800}
    \begin{document}
    \begin{tabular}{ |s|p{3cm}|p{3cm}|  }
    \hline
    \rowcolor{lightgray} \multicolumn{3}{|c|}{Country List} \\
    \hline
    Country Name    or Area Name& ISO ALPHA 2 Code &ISO ALPHA 3 \\
    \hline
    Afghanistan & AF &AFG \\
    \rowcolor{gray}
    Aland Islands & AX & ALA \\
    Albania   &AL & ALB \\
    Algeria  &DZ & DZA \\
    American Samoa & AS & ASM \\
    Andorra & AD & \cellcolor[HTML]{AA0044} AND    \\
    Angola & AO & AGO \\
    \hline
    \end{tabular}

    \end{document}
    {% endcall %}
    </p>

Prerequsites
^^^^^^^^^^^^
* ``TexLive``
    - For installation of TexLive. See `Instructions on TUG <https://www.tug.org/texlive/doc/texlive-en/texlive-en.html#installation>`_.
    - For Linux platform
        - Vanilla TexLive is preferable if you want to use latest version of TexLive and not to bother upgrading packages.
        - If you don't mind use outdated version of TexLive, you can also install the version comes with Linux distributed by::

            sudo apt-get install texlive-full

* ``latexmk``, required, shipped with TexLive full installation, version >= 4.39 is required.
* ``dvisvgm``, optional, shipped with TexLive full installation.
* ``dvipng``, required, shipped with TexLive full installation.
* ``ImageMagick``
    - For Windows platform, install with option ``install legacy component`` ticked.

Configurations
^^^^^^^^^^^^^^
In your ``local_settings.py``:

* Enable Latex to image functionality: set ``RELATE_LATEX_TO_IMAGE_ENABLED = True``, required.
* Set latex bin path: set ``RELATE_LATEX_BIN_PATH`` to the bin path of the TexLive installation. For example, ``/usr/local/texlive/2015/bin/x86_64-linux``. ``latexmk``, ``dvisvgm`` and ``dvipng`` should be found in that directory.
* Set ImageMagick bin path: set ``RELATE_IMAGEMAGICK_BIN_DIR`` to the absolute path of the location of the bin ``convert`` (``convert.exe`` for Windows) of your ImageMagick installation. This is required for Windows since Windows itself has another cmd named ``convert``.
* Set max cache bytes for generated images by configuring ``IMAGE_CACHE_MAX_BYTES``.

Usage
^^^^^

.. autofunction:: tex_to_img_tag

* Required args:
    - ``compiler``: string, the command line used to compile the tex file, currently available: ``xelatex``, ``pdflatex``, ``latex`` and ``lualatex``.
    - ``image_format``: string, the output format of the image, only ``png`` and ``svg`` are available for now.

    .. note::
        * Output with ``svg`` format only support ``latex`` as compiler. If ``compiler="latex"``.
        * If the code contains figure using ``tikz/pgf`` , the image_format will be forced using ``svg``.


* Optional:
    - ``tex_filename``: string, the based filename of the latex,  and image as well, if not set, use md5 of the full latex code
    - ``tex_preamble``: string, which allows user move the preamble part of the latex code out of the ``latex`` macro. For example, we can use ``{% set foo %}{% endset %}`` block to define ``foo`` as the preamble and then use ``tex_premable=foo`` as an argument of the ``latex`` caller. Those definitions can also be saved as macros in the course repo. That is a good practice for latex code with common preambles. However, this should be used with cautiousness, as changing of the preamble definition will force all the originally valid images, whose preambles have been changed, to be recompiled, which might result in failure (same for ``tex_preamble_extra``). For latex code that might be changed in the future, the best practice is to keep full latex document in the page markup.
    - ``tex_preamble_extra``: string, more packages or settings appended to ``tex_premable``.
    - ``force_regenerate``: boolean, if True, regenerate image if it exists, default: False(recommended).
    - ``html_class_extra``: string, extra html class for the ``<img>`` tag, besides ``img-responsive``
    - ``alt``: string, brief description of the image, default: the document part of the tex source.


.. note::

    ``{{``, ``}}``, ``{%``, ``%}``, ``{#`` and ``#}`` are used as marking strings in jinja template, latex code submitted (including preabmle part and self-defined commands) should avoid containing those strings, or jinja will just fail to render. The work around is to manually insert a space (spaces or tabs) between the two character (e.g., ``{{`` --> ``{  {``) for each of those strings appeared in latex code.

A more sophisticated example can be found at `relate-example<https://github.com/inducer/relate-sample/pull/4>`_.