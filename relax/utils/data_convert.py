#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import re


def convert_sohu_img(content):
    pat = r'<img src="(.*\.)(jpg|png|gif)" class=.*data-src="(.*\.)(jpg|png|gif)" \tonload=.*</a>'
    content_sp = re.split(r'<div class="centerImg">', content)
    result = []

    def rep_img(m):
        return '<img class="lazy" alt="" src="%s" data-original="%s"\
            style="display:inline;"/><noscript><img src="%s"/></noscript><br/>\
            </a>' % (m.group(3)+m.group(4), m.group(3), m.group(4))

    for data in content_sp:
        result.append(re.sub(pat, rep_img, data))

    return '<div class="centerImg">'.join(result)


def convert_163(content, img_list):
    pat = u"(<!--IMG#\d+-->)"
    data = re.split(pat, content)  # remove the last item 声明内容
    for v in img_list:
        if v['ref'] in data:
            pos = data.index(v['ref'])
            rep_img = '<img class="lazy" alt="%s" src="%s" data-original="%s"\
                style="display:inline;" /><noscript><img alt="%s" src="%s" />\
                </noscript><br />' % (v['alt'], v['src'], v['src'], v['alt'],
                                      v['src'])
            data[pos] = rep_img
    return ' '.join(data)
