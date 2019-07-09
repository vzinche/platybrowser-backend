import unittest
import os
import sys
import json
from shutil import rmtree

import numpy as np
import pandas
import h5py
from cluster_tools.node_labels import NodeLabelWorkflow
sys.path.append('../..')


# check new version of gene mapping against original
class TestCellNucleusMapping(unittest.TestCase):
    tmp_folder = 'tmp'

    def _tearDown(self):
        try:
            rmtree(self.tmp_folder)
        except OSError:
            pass

    def test_cell_nucleus_mappings(self):
        from scripts.attributes.cell_nucleus_mapping import map_cells_to_nuclei

        segmentation_folder = '../../data/0.1.1/segmentations'
        seg_path = os.path.join(segmentation_folder,
                                'sbem-6dpf-1-whole-segmented-cells-labels.h5')
        segmentation_folder = '../../data/0.0.0/segmentations'
        nuc_path = os.path.join(segmentation_folder,
                                'sbem-6dpf-1-whole-segmented-nuclei-labels.h5')
        with h5py.File(seg_path, 'r') as f:
            max_id = f['t00000/s00/0/cells'].attrs['maxId']
        label_ids = np.arange(max_id + 1, dtype='uint64')

        output_path = os.path.join(self.tmp_folder, 'table-test.csv')

        config_folder = os.path.join(self.tmp_folder, 'configs')
        os.makedirs(config_folder, exist_ok=True)

        conf = NodeLabelWorkflow.get_config()['global']
        shebang = '#! /g/kreshuk/pape/Work/software/conda/miniconda3/envs/cluster_env37/bin/python'
        conf.update({'shebang': shebang})
        with open(os.path.join(config_folder, 'global.config'), 'w') as f:
            json.dump(conf, f)

        target = 'local'
        max_jobs = 60
        map_cells_to_nuclei(label_ids, seg_path, nuc_path, output_path,
                            tmp_folder=self.tmp_folder, target=target, max_jobs=max_jobs)

        table = pandas.read_csv(output_path, sep='\t')
        assert len(table) == max_id + 1

        # base_path = '../../data/0.0.0/tables/sbem-6dpf-1-whole-segmented-cells-labels/default.csv'
        # base_table = pandas.read_csv(base_path, sep='\t')

        # seg_key = 't00000/s00/2/cells'
        # tissue_path = '../../data/rawdata/sbem-6dpf-1-whole-segmented-tissue-labels.h5'
        # tissue_key = 't00000/s00/0/cells'
        # self.check_result(table, base_table,
        #                   seg_path, seg_key,
        #                   tissue_path, tissue_key)


if __name__ == '__main__':
    unittest.main()
