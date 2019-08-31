from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def add_questions_groups_to_survey_form(form, survey):
    from lxml import etree

    html_output = ''
    added_groups = list()
    questions = survey.question_set.all()

    for f in form.split('</div>'):
        div_formgroup = f + "</div>"
        html = etree.HTML(div_formgroup)
        if html is not None:
            input_xpath = html.xpath('//div[@class="form-group"]//input/@name')
            question_id = input_xpath[0].replace('qid_', '')
            question_group = questions.get(id=question_id).question_group

            if question_group not in added_groups:
                added_groups.append(question_group)
                html_output += '<div class="survey__group-name">%s</div>' % question_group

        html_output += div_formgroup

    return mark_safe(html_output)
