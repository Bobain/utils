from pandas_highcharts.core import serialize
import pandas, jinja2
from jinja2 import Environment, PackageLoader, DebugUndefined
env = Environment(loader=PackageLoader('utils', 'html'))
env4add = Environment(undefined=DebugUndefined,loader=PackageLoader('utils', 'html'))

def get_menu_links_from_dict(d, str_pre_k='', flat_menu=False, inc_indent = '', prefix_link = ""):
    menu_links = ''
    other_links = ''
    for k, curr_d in d.iteritems():
        if isinstance(curr_d, dict):
            id_ = str_pre_k + "\n" + inc_indent + k # .replace(' ','_')
            c_first_links, c_other_links  = get_menu_links_from_dict(curr_d, id_, flat_menu=flat_menu,
                                                                     inc_indent=inc_indent + "\t")
            if flat_menu:
                menu_links += c_first_links
            else:
                other_links += ' <div class="list-group submenu" id="ml_%s"> \n' % id_ + \
                                    c_first_links + \
                                    '\n</div>\n' + c_other_links
                menu_links += ' <a href="#ml_%s" class="list-group-item">%s</a> \n' % (id_,k)
        elif isinstance(curr_d, basestring):
            if flat_menu:
                menu_links += ' <li> <a href="%s">%s</a> </li>\n' % (prefix_link+curr_d, str_pre_k + " " + k)
            else:
                menu_links += ' <a href="%s" class="list-group-item">%s</a> \n' % (prefix_link+curr_d,k)
        else:
            raise Exception('values mues be dict or strings')
    return (menu_links, other_links)


def get_web_page_with_side_menu(side, **args):
    assert side in ['right', 'left', 'both']
    template = env4add.get_template('template.html')
    header = '{{header}}  \n <script type="text/javascript"> \n' + \
                    ' $(document).ready(function(){ \n'
    for s in ['left', 'right']:
        if side in [s, 'both']:
            template = jinja2.Template(template.render(prebody = '{{prebody}}\n' +
                                   env4add.get_template("side_menu_body.html")
                                               .render(menu_name= s + '_menu',
                                                      menu_links= '{{' + s + '_menu_links}}',
                                                      sublists_elements='{{' + s + '_menu_sublinks}}')),
                                       undefined=DebugUndefined)
            header += " $('#%s_menu').BootSideMenu({side:'%s'}); \n" %(s, s)
    header += ' }); </script>'
    template = jinja2.Template(template.render(header='{{header}}\n'+header))
    return template.render(**args)

def get_web_page_html(**args):
    return env.get_template('template.html').render(**args)

def get_basic_chart(name, df, title=None, add_args=None):
        if add_args is None:
            add_args = {}
        chart_template_func = \
            '<script type="text/javascript">'+  \
            'var chart1; // globally available\n' + \
            ' $(function() {\n' + \
            "      $('#%s').highcharts(%s);\n " + \
            '   });\n' + \
            ' </script> \n'
        d = serialize(df,output_type="dict", render_to=name, title=title)
        d['chart']['zoomType'] = 'x'
        d['subtitle'] = {'text':'Click and drag in the plot area to zoom in. Click on the name of a serie to remove/add it'}
        return chart_template_func % (name,pandas.io.json.dumps(d))


# def get_stock_chart(name, df, title=None, add_args=None):
#     template_stock_chart  = \
#         ' <script type="text/javascript"> \n' + \
#         ' var chart1; \n' + \
#         "     $(function() {\n" + \
#         "       chart1 = new Highcharts.StockChart(%s); \n" + \
#         ' });  \n' + \
#         ' </script> '
#
#     chartdict = {
#             'chart': {"renderTo": name},
#             'rangeSelector': {'selected': 1},
#              'series': [{'name' : "blah",
#                          'data': zip([unix_time_millis(ts) for ts in df.index], df['all'].values.tolist()),
#                          }]}
#     return template_stock_chart % json.dumps(chartdict)
#     # return template_stock_chart.format(chart=name, data=serialize(df,output_type="json", render_to=name, title=title))


def get_include_chart_str(chart_name, df, title):
    return (' <div id="%s" style="width:100%%; height:600px"></div> \n'  \
                 % (chart_name) )+  \
            get_basic_chart(chart_name, df, title=title)