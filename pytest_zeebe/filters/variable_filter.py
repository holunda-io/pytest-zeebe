
class VariableRecordFilter:
    def __init__(self, records):
        self.records = [record for record in records if record["valueType"] == "VARIABLE"]

    def with_process_instance_key(self, process_instance_key):
        return VariableRecordFilter(
            [record for record in self.records if record['value']['processInstanceKey'] == process_instance_key])

    def with_rejection_type(self, rejection_type):
        return VariableRecordFilter(
            [record for record in self.records if record['rejectionType'] == rejection_type])