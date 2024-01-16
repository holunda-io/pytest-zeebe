import json

from pytest_zeebe.filters.incident_filter import IncidentRecordFilter
from pytest_zeebe.filters.process_instance_filter import ProcessInstanceRecordFilter
from pytest_zeebe.filters.process_message_subscription_filter import ProcessMessageSubscriptionRecordFilter
from pytest_zeebe.filters.variable_filter import VariableRecordFilter


class ProcessInstanceAssert:

    def __init__(self, process_instance_key, record_stream):
        self.process_instance_key = process_instance_key
        self.record_stream = record_stream

    def is_started(self):
        is_started = any(ProcessInstanceRecordFilter(self.record_stream)
                         .with_process_instance_key(self.process_instance_key)
                         .with_rejection_type('NULL_VAL')
                         .with_intent('ELEMENT_ACTIVATED')
                         .with_bpmn_element_type('PROCESS')
                         .records)
        assert is_started, f"Process with key {self.process_instance_key} was not started."
        return self

    def is_active(self):
        is_active = not any(record['intent'] in ['ELEMENT_COMPLETED', 'ELEMENT_TERMINATED'] for record in
                            ProcessInstanceRecordFilter(self.record_stream)
                            .with_process_instance_key(self.process_instance_key)
                            .with_rejection_type('NULL_VAL')
                            .with_bpmn_element_type('PROCESS')
                            .records)
        assert is_active, f"Process with key {self.process_instance_key} is not active."
        return self

    def is_completed(self):
        completed = any(ProcessInstanceRecordFilter(self.record_stream)
                        .with_process_instance_key(self.process_instance_key)
                        .with_rejection_type('NULL_VAL')
                        .with_bpmn_element_type('PROCESS')
                        .with_intent('ELEMENT_COMPLETED')
                        .records)
        assert completed, f"Process instance {self.process_instance_key} was not completed."
        return self

    def is_not_completed(self):
        not_completed = not any(ProcessInstanceRecordFilter(self.record_stream)
                                .with_process_instance_key(self.process_instance_key)
                                .with_rejection_type('NULL_VAL')
                                .with_bpmn_element_type('PROCESS')
                                .with_intent('ELEMENT_COMPLETED')
                                .records)
        assert not_completed, f"Process with key {self.process_instance_key} was completed."
        return self

    def is_terminated(self):
        is_terminated = any(ProcessInstanceRecordFilter(self.record_stream)
                            .with_process_instance_key(self.process_instance_key)
                            .with_rejection_type('NULL_VAL')
                            .with_bpmn_element_type('PROCESS')
                            .with_intent('ELEMENT_TERMINATED')
                            .records)
        assert is_terminated, f"Process with key {self.process_instance_key} was not terminated."
        return self

    def is_not_terminated(self):
        not_terminated = not any(ProcessInstanceRecordFilter(self.record_stream)
                                 .with_process_instance_key(self.process_instance_key)
                                 .with_rejection_type('NULL_VAL')
                                 .with_bpmn_element_type('PROCESS')
                                 .with_intent('ELEMENT_TERMINATED')
                                 .records)
        assert not_terminated, f"Process with key {self.process_instance_key} was terminated."
        return self

    def has_passed_element(self, element_id, times=1):
        count = sum(1 for _ in ProcessInstanceRecordFilter(self.record_stream)
                    .with_process_instance_key(self.process_instance_key)
                    .with_rejection_type('NULL_VAL')
                    .with_element_id(element_id)
                    .with_intents('ELEMENT_COMPLETED', 'SEQUENCE_FLOW_TAKEN')
                    .records)
        assert count == times, f"Expected element with id {element_id} to be passed {times} times, but was {count}."
        return self

    def has_not_passed_element(self, element_id):
        return self.has_passed_element(element_id, times=0)

    def has_passed_elements_in_order(self, *element_ids):
        found_element_records = [record['value']['elementId'] for record in
                                 ProcessInstanceRecordFilter(self.record_stream)
                                 .with_process_instance_key(self.process_instance_key)
                                 .with_rejection_type('NULL_VAL')
                                 .with_element_id_in(*element_ids)
                                 .with_intents('ELEMENT_COMPLETED', 'SEQUENCE_FLOW_TAKEN')
                                 .records]
        assert found_element_records == list(element_ids), "Ordered elements do not match."
        return self

    def is_waiting_at_elements(self, *element_ids):
        elements_in_wait_state = self.get_elements_in_wait_state()
        assert set(element_ids).issubset(elements_in_wait_state), "Not all elements are in wait state."
        return self

    def is_not_waiting_at_elements(self, *element_ids):
        elements_in_wait_state = self.get_elements_in_wait_state()
        assert not set(element_ids).intersection(elements_in_wait_state), "Some elements are in wait state."
        return self

    def get_elements_in_wait_state(self):
        elements_in_wait_state = set()
        for record in (ProcessInstanceRecordFilter(self.record_stream)
                        .with_process_instance_key(self.process_instance_key)
                        .with_rejection_type('NULL_VAL')
                        .without_bpmn_element_type('PROCESS')
                        .records):
            if record['intent'] == 'ELEMENT_ACTIVATED':
                elements_in_wait_state.add(record['value']['elementId'])
        return elements_in_wait_state

    def is_waiting_exactly_at_elements(self, *element_ids):
        elements_in_wait_state = self.get_elements_in_wait_state()
        wrongfully_waiting_element_ids = [id for id in elements_in_wait_state if id not in element_ids]
        wrongfully_not_waiting_element_ids = [id for id in element_ids if id not in elements_in_wait_state]

        assert not wrongfully_waiting_element_ids, f"Process with key {self.process_instance_key} is waiting at element(s) with id(s) {', '.join(wrongfully_waiting_element_ids)}"
        assert not wrongfully_not_waiting_element_ids, f"Process with key {self.process_instance_key} is not waiting at element(s) with id(s) {', '.join(wrongfully_not_waiting_element_ids)}"
        return self

    def is_waiting_for_messages(self, *message_names):
        open_message_subscriptions = self.get_open_message_subscriptions()
        assert set(message_names).issubset(open_message_subscriptions), "Not all messages are in open subscriptions."
        return self

    def is_not_waiting_for_messages(self, *message_names):
        open_message_subscriptions = self.get_open_message_subscriptions()
        assert not set(message_names).intersection(open_message_subscriptions), "Some messages are in open subscriptions."
        return self

    def get_open_message_subscriptions(self):
        open_message_subscriptions = set()
        for record in (ProcessMessageSubscriptionRecordFilter(self.record_stream)
            .with_process_instance_key(self.process_instance_key)
            .with_rejection_type('NULL_VAL')
            .records):
            if record['intent'] in ['CREATING', 'CREATED']:
                open_message_subscriptions.add(record['value']['messageName'])
        return open_message_subscriptions

    def has_correlated_message_by_name(self, message_name, times):
        actual_times = sum(1 for record in ProcessMessageSubscriptionRecordFilter(self.record_stream)
                           .with_process_instance_key(self.process_instance_key)
                           .with_rejection_type('NULL_VAL')
                           .with_message_name(message_name)
                           .with_intent('CORRELATED')
                           .records)
        assert actual_times == times, f"Expected message with name '{message_name}' to be correlated {times} times, but was {actual_times} times"
        return self

    def has_correlated_message_by_correlation_key(self, correlation_key, times):
        actual_times = sum(1 for record in ProcessMessageSubscriptionRecordFilter(self.record_stream)
                           .with_process_instance_key(self.process_instance_key)
                           .with_rejection_type('NULL_VAL')
                           .with_correlation_key(correlation_key)
                           .with_intent('CORRELATED')
                           .records)
        assert actual_times == times, f"Expected message with correlation key '{correlation_key}' to be correlated {times} times, but was {actual_times} times"
        return self

    def has_variable(self, name):
        variables = self.get_process_instance_variables()
        assert name in variables, f"Variable '{name}' not found."
        return self

    def has_variable_with_value(self, name, value):
        variables = self.get_process_instance_variables()
        actual_value = json.loads(variables.get(name))
        assert actual_value == value, f"Variable '{name}' does not have the expected value."
        return self

    def get_process_instance_variables(self):
        return {record['value']['name']: record['value']['value'] for record in
                VariableRecordFilter(self.record_stream)
                .with_process_instance_key(self.process_instance_key)
                .with_rejection_type('NULL_VAL')
                .records}

    def has_any_incidents(self):
        incidents_were_raised = any(True for _ in IncidentRecordFilter(self.record_stream)
                                    .with_rejection_type('NULL_VAL')
                                    .with_intent('CREATED')
                                    .with_process_instance_key(self.process_instance_key)
                                    .records)
        assert incidents_were_raised, "No incidents were raised for this process instance"
        return self

    def has_no_incidents(self):
        incidents_were_raised = any(True for _ in IncidentRecordFilter(self.record_stream)
                                    .with_rejection_type('NULL_VAL')
                                    .with_intent('CREATED')
                                    .with_process_instance_key(self.process_instance_key)
                                    .records)
        assert not incidents_were_raised, "Incidents were raised for this process instance"
        return self

    # todo implement IncidentAssert
    # def extracting_latest_incident(self):
    #     self.has_any_incidents()
    #     incident_created_records = [record for record in IncidentRecordFilter(self.record_stream)
    #                                 .with_rejection_type('NULL_VAL')
    #                                 .with_intent('CREATED')
    #                                 .with_process_instance_key(self.process_instance_key)
    #                                 .records]
    #     latest_incident_record = incident_created_records[-1]
    #     return IncidentAssert(latest_incident_record['key'], self.record_stream)

    def extracting_latest_called_process(self):
        self.has_called_process()
        latest_called_process_record = [record for record in ProcessInstanceRecordFilter(self.record_stream)
                                        .with_parent_process_instance_key(self.process_instance_key)
                                        .records][-1]
        return ProcessInstanceAssert(latest_called_process_record['key'], self.record_stream)

    def extracting_latest_called_process_with_id(self, process_id):
        self.has_called_process_with_id(process_id)
        latest_called_process_record = [record for record in ProcessInstanceRecordFilter(self.record_stream)
                                        .with_parent_process_instance_key(self.process_instance_key)
                                        .with_bpmn_process_id(process_id)
                                        .records][-1]
        return ProcessInstanceAssert(latest_called_process_record['key'], self.record_stream)

    def has_called_process(self):
        has_called_process = any(True for _ in ProcessInstanceRecordFilter(self.record_stream)
                                 .with_parent_process_instance_key(self.process_instance_key)
                                 .records)
        assert has_called_process, "No process was called from this process"
        return self

    def has_not_called_process(self):
        called_processes = {record['value']['bpmnProcessId'] for record in ProcessInstanceRecordFilter(self.record_stream)
                            .with_parent_process_instance_key(self.process_instance_key)
                            .records}
        assert not called_processes, f"A process was called from this process, distinct called processes are: {', '.join(called_processes)}"
        return self

    def has_called_process_with_id(self, process_id):
        has_called_process = any(True for record in ProcessInstanceRecordFilter(self.record_stream)
                                 .with_parent_process_instance_key(self.process_instance_key)
                                 .with_bpmn_process_id(process_id)
                                 .records)
        assert has_called_process, f"No process with id `{process_id}` was called from this process"
        return self

    def has_not_called_process_with_id(self, process_id):
        has_called_process = any(True for record in ProcessInstanceRecordFilter(self.record_stream)
                                 .with_parent_process_instance_key(self.process_instance_key)
                                 .with_bpmn_process_id(process_id)
                                 .records)
        assert not has_called_process, f"A process with id `{process_id}` was called from this process"
        return self

    def get_called_process_records(self):
        return ProcessInstanceRecordFilter(self.record_stream).with_parent_process_instance_key(
            self.process_instance_key
        )
