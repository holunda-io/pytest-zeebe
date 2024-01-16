
class ProcessMessageSubscriptionRecordFilter:
    def __init__(self, records):
        self.records = [record for record in records if record["valueType"] == "PROCESS_MESSAGE_SUBSCRIPTION"]

    def with_process_instance_key(self, process_instance_key):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['value']['processInstanceKey'] == process_instance_key])

    def with_message_name(self, message_name):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['value']['messageName'] == message_name])

    def with_correlation_key(self, correlation_key):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['value']['correlationKey'] == correlation_key])

    def with_rejection_type(self, rejection_type):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['rejectionType'] == rejection_type])

    def with_intent(self, intent):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['intent'] == intent])

    def with_message_key(self, message_key):
        return ProcessMessageSubscriptionRecordFilter(
            [record for record in self.records if record['value']['messageKey'] == message_key])