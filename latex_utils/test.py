from utils.latex_utils import latex_jinja_env, _file_write

template = latex_jinja_env.get_template('/utils/jinja-test.tex')
tex=template.render(section1='Long Form', section2='Short Form')

_file_write("test.tex", tex)

template = latex_jinja_env.get_template('lp_form.tex')
tex=template.render(section1='Long Form', section2='Short Form')

_file_write("test2.tex", tex.encode('UTF-8'))
