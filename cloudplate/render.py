import yaml

TEMPLATE_BASE = {'AWSTemplateFormatVersion': '2010-09-09'}


def render_cloudlet(jenv, cloudlet_def):
    if cloudlet_def[1]:
        name = cloudlet_def[1].get('name', cloudlet_def[0])
        template_path = cloudlet_def[1].get('template', cloudlet_def[0] + '.yaml')
        parameters = cloudlet_def[1].get('parameters', {})
    else:
        name = cloudlet_def[0]
        template_path = cloudlet_def[0] + '.yaml'
        parameters = {}
    template = jenv.get_template(template_path)
    return {name: yaml.safe_load(template.render(**parameters))}


def render_template(jenv, template_def):
    name, template_options = template_def
    if 'cloudlets' not in template_options:
        raise NoCloudletsError(template_def)
    cloudlets = template_options['cloudlets']
    if not isinstance(cloudlets, dict):
        raise MalformedTemplateError(template_def, "bad cloudlets definition")
    if not cloudlets:
        raise NoCloudletsError(template_def)
    cloudlet_defs = cloudlets.items()
    template = TEMPLATE_BASE.copy()
    resources = {}
    for cloudlet_def in cloudlet_defs:
        resources.update(render_cloudlet(jenv, cloudlet_def))
    template['Resources'] = resources
    return template


class MalformedTemplateError(Exception):
    def __init__(self, template_def, reason):
        self.reason = reason
        self.template_def = template_def

    def __str__(self):
        return "Template {}:{} {0}".format(self.reason, *self.template_def)


class NoCloudletsError(MalformedTemplateError):
    def __init__(self, template_def):
        super(NoCloudletsError, self).__init__(template_def, "has no cloudlets")