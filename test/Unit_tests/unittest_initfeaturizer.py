import unittest
import sys
sys.path.append("../..")
from holoclean.holoclean import HoloClean, Session
from holoclean.errordetection.sql_dcerrordetector import SqlDCErrorDetection
from holoclean.featurization.initfeaturizer import SignalInit
from pyspark.sql.types import *

holo_obj = HoloClean(
            holoclean_path="../..",
            verbose=True,
            timing_file='execution_time.txt',
            learning_iterations=50,
            learning_rate=0.001,
            batch_size=20)


class TestInitFeaturizer(unittest.TestCase):
    def setUp(self):

        self.session = Session(holo_obj)
        self.dataset = "../../datasets/unit_test/unit_test_dataset.csv"
        self.session.load_data(self.dataset)
        self.session.load_denial_constraints(
            "../../datasets/unit_test/unit_test_constraints.txt")

        detector = SqlDCErrorDetection(self.session)
        self.session.detect_errors([detector])
        self.session._ds_domain_pruning(0.5)

        self.init_signal = SignalInit(self.session)


    def tearDown(self):
        del self.session

    def test_Init_query_for_clean(self):
        query = self.init_signal.get_query()[0]

        Int_feature_dataframe = \
            holo_obj.dataengine.query(query, 1)

        anticipated_Init_feature_C_clean_cells = [
            ["1", "2", "1", "1"], ["2", "1", "1", "1"]]
        anticipated_dataframe = holo_obj.spark_session.createDataFrame(
            anticipated_Init_feature_C_clean_cells, StructType([
                StructField("vid", StringType(), False),
                StructField("assigned_val", StringType(), False),
                StructField("feature", StringType(), False),
                StructField("count", StringType(), False),
            ]))
        incorrect = anticipated_dataframe.subtract(
            Int_feature_dataframe)
        self.assertEquals(incorrect.count(), 0)

    def test_Init_query_for_dk(self):
        query = self.init_signal.get_query(0)[0]
        Int_feature_dataframe = \
            holo_obj.dataengine.query(query, 1)

        anticipated_Init_feature_C_dk_cells = [["1", "1", "1", "1"],
                                               ["2", "1", "1", "1"],
                                               ["3", "1", "1", "1"],
                                               ["4", "1", "1", "1"],
                                               ["5", "1", "1", "1"],
                                               ["6", "1", "1", "1"],
                                               ["7", "1", "1", "1"],
                                               ["8", "1", "1", "1"],
                                               ["9", "1", "1", "1"],
                                               ["10", "1", "1", "1"]]
        anticipated_dataframe = holo_obj.spark_session.createDataFrame(
            anticipated_Init_feature_C_dk_cells, StructType([
                StructField("vid", StringType(), False),
                StructField("assigned_val", StringType(), False),
                StructField("feature", StringType(), False),
                StructField("count", StringType(), False),
            ]))
        incorrect = anticipated_dataframe.subtract(
            Int_feature_dataframe)
        self.assertEquals(incorrect.count(), 0)


if __name__ == "__main__":
    unittest.main()
