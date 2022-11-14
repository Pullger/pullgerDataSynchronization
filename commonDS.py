import importlib


def get_model_class_by_name(full_path):
    path_list = full_path.split('.')
    module_library = importlib.import_module('.'.join(path_list[:-1]))
    return getattr(module_library, path_list[-1])
