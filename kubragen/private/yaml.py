from yaml.representer import SafeRepresenter


def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar
    return new_representer


represent_single_quoted_str = change_style("'", SafeRepresenter.represent_str)
represent_double_quoted_str = change_style('"', SafeRepresenter.represent_str)
represent_folded_str = change_style('>', SafeRepresenter.represent_str)
represent_literal_str = change_style('|', SafeRepresenter.represent_str)
