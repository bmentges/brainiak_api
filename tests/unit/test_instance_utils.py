from unittest import TestCase
from brainiak.instance.utils import are_there_label_properties_in


class RdfsLabelValidationTestCase(TestCase):

    def test_exists_label_property(self):
        instance_data = {
            u'rdfs:label': "a label",
            u"a:property": "a value"
        }
        self.assertTrue(are_there_label_properties_in(instance_data))

    def test_does_not_exist_label_property(self):
        instance_data = {
            u"a:property": "a value"
        }
        self.assertFalse(are_there_label_properties_in(instance_data))
