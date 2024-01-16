
class ProcessInstanceRecordFilter:
    def __init__(self, records):
        self.records = [record for record in records if record["valueType"] == "PROCESS_INSTANCE"]

    def with_process_instance_key(self, process_instance_key):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['processInstanceKey'] == process_instance_key])

    def with_bpmn_element_type(self, bpmn_element_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['bpmnElementType'] == bpmn_element_type])

    def without_bpmn_element_type(self, bpmn_element_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['bpmnElementType'] != bpmn_element_type])

    def with_bpmn_event_type(self, bpmn_event_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['bpmnEventType'] == bpmn_event_type])

    def without_bpmn_event_type(self, bpmn_event_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['bpmnEventType'] != bpmn_event_type])

    def with_intent(self, intent):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['intent'] == intent])

    def with_intents(self, *intents):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['intent'] in intents])

    def with_element_id(self, element_id):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['elementId'] == element_id])

    def with_element_id_in(self, *element_ids):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['elementId'] in element_ids])

    def with_rejection_type(self, rejection_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['rejectionType'] == rejection_type])

    def with_parent_process_instance_key(self, parent_process_instance_key):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['parentProcessInstanceKey'] == parent_process_instance_key])

    def with_bpmn_process_id(self, bpmn_process_id):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['value']['bpmnProcessId'] == bpmn_process_id])

    def with_record_type(self, record_type):
        return ProcessInstanceRecordFilter(
            [record for record in self.records if record['recordType'] == record_type])
