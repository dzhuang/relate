{%- extends 'basic.tpl' -%}

{# This is changed to prevent code_cell being process by markdown twice #}

{% block input %}<pre class="relate_tmp_pre">{{ super() }}</pre>
{%- endblock input %}

{% block empty_in_prompt -%}
{%- endblock empty_in_prompt %}