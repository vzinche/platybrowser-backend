import os
from . import attributes
from .export import export_segmentation
from .files import add_image, add_segmentation, copy_tables
from .files.copy_helper import copy_file


def is_image(data, check_source):
    if check_source and 'source' not in data:
        return False
    if 'name' in data and 'input_path' in data:
        return True
    return False


def is_static_segmentation(data, check_source):
    if check_source and 'source' not in data:
        return False
    if 'name' in data and 'segmentation_path' in data:
        return True
    return False


def is_dynamic_segmentation(data, check_source):
    if check_source and 'source' not in data:
        return False
    if 'name' in data and 'paintera_project' in data and 'resolution' in data:
        if len(data['paintera_project']) != 2 or len(data['resolution']) != 3:
            return False
        return True
    return False


def check_inputs(new_data, check_source=True):
    if not all(isinstance(data, dict) for data in new_data):
        raise ValueError("Expect list of dicts as input")

    for data in new_data:
        if not any(is_image(data, check_source), is_static_segmentation(data, check_source), is_dynamic_segmentation(data, check_source)):
            raise ValueError("Could not parse input element %s" % str(data))


def add_data(data, folder, target, max_jobs, source=None):
    source = data['source'] if source is None else source
    name = data['name']
    full_name = '%s-%s' % (source, name)
    file_name = '%s.xml' % full_name

    is_private = data.get('is_private', False)
    check_source = source is None

    if is_image(data, check_source):
        # register the image data
        add_image(source, name, data['input_path'],
                  is_private=is_private)

        # copy image data from the raw folder to new release folder
        xml_raw = os.path.join('data/raw', file_name)
        xml_out = os.path.join(folder, file_name)
        copy_file(xml_raw, xml_out)

    elif is_static_segmentation(data, check_source):
        # register the static segmentation
        table_path_dict = data.get('table_path_dict', None)
        add_segmentation(source, name,
                         segmentation_path=data['segmentation_path'],
                         table_path_dict=table_path_dict,
                         is_private=is_private)

        # copy segmentation data from the raw folder to new release folder
        xml_raw = os.path.join('data/raw', file_name)
        xml_out = os.path.join(folder, file_name)
        copy_file(xml_raw, xml_out)

        # if we have tables, copy them as well
        if table_path_dict is not None:
            copy_tables('data/raw', os.path.join(folder, 'tables'), full_name)

    elif is_dynamic_segmentation(data, check_source):
        # register the dynamic segmentation
        paintera_project = data['paintera_project']
        resolution = data['resolution']
        table_update_function = data.get('table_update_function', None)
        add_segmentation(source, name,
                         paintera_project=paintera_project,
                         resolution=resolution,
                         table_update_function=table_update_function,
                         is_private=is_private)

        # export segmentation data to new release folder
        paintera_root, paintera_key = paintera_project
        tmp_folder = 'tmp_export_%s' % full_name
        export_segmentation(paintera_root, paintera_key,
                            None, folder, full_name,
                            resolution=resolution,
                            tmp_folder=tmp_folder,
                            target=target, max_jobs=max_jobs)

        # if we have a table update function, call it
        if table_update_function is not None:
            tmp_folder = 'tmp_tables_%s' % name
            update_function = getattr(attributes, table_update_function)
            update_function(folder, name, tmp_folder, resolution,
                            target=target, max_jobs=max_jobs)
