
class IncidentRecordFilter:
    def __init__(self, records):
        self.records = [record for record in records if record["valueType"] == "INCIDENT"]

    def with_incident_key(self, incident_key):
        return IncidentRecordFilter(
            [record for record in self.records if record['key'] == incident_key])

    def with_rejection_type(self, rejection_type):
        return IncidentRecordFilter(
            [record for record in self.records if record['rejectionType'] == rejection_type])

    def with_process_instance_key(self, process_instance_key):
        return IncidentRecordFilter(
            [record for record in self.records if record['value']['processInstanceKey'] == process_instance_key])

    def with_job_key(self, job_key):
        return IncidentRecordFilter(
            [record for record in self.records if record['value']['jobKey'] == job_key])

    def with_intent(self, intent):
        return IncidentRecordFilter(
            [record for record in self.records if record['intent'] == intent])