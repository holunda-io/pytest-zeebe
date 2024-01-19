# pytest-zeebe
*Pytest fixtures for testing Camunda 8 processes in Python using a Zeebe test engine.*

![Compatible with: Camunda Platform 8](https://img.shields.io/badge/Compatible%20with-Camunda%20Platform%208-26d07c)
[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-RED.svg)](https://holisticon.de/)


## 🚀 What does it do?
This package provides a set of fixtures to set up Zeebe process tests for Python in no time:
- automatically spins up a stripped-down Zeebe engine per file/module (same as used by [zeebe-process-test](https://github.com/camunda/zeebe-process-test/)) 
- resets engine state before every test
- injects a ZeebeTestClient to drive the process
- (optionally) injects a ZeebeTestEngine to await idle state or access raw zeebe records
- provides rich assertions for the process instance (goal: equal to zeebe-process-test BpmnAssertions)

## Install
```
pip install pytest-zeebe
```


## Example Usage
The engine is reset before every test, so you can create a fixture to deploy your process automatically:
```python
@pytest.fixture(autouse=True)
def deploy(zeebe_test_client: ZeebeTestClient):
    zeebe_test_client.deploy_process("test.bpmn")
```

With the process deployed, you can start it, complete tasks and make assertions as usual:
```python
def test(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "var": "A"
    }

    # when
    # -> start
    process_instance = zeebe_test_client.create_process_instance("TestProcess", variables=variables)

    # -> complete Task A
    zeebe_test_client.complete_task("taskA")
    
    assert_that(process_instance).is_waiting_at_elements("TaskC")

    # -> complete Task C
    zeebe_test_client.complete_task("taskC", variables={"resultC": True})

    # then
    assert_that(process_instance) \
        .is_completed() \
        .has_passed_elements_in_order("StartEvent_1", "TaskA", "TaskC", "EndEvent_1") \
        .has_variable_with_value("var", "A") \
        .has_variable_with_value("resultC", True) \
        .has_no_incidents()
```

## Known Issues
This package ships with its own grpc zeebe client. Due to the inner workings of protobuf, this will lead to an unresolvable conflict if you also import code from another library that also registers protobuf descriptors for the zeebe gateway protocol (like pyzeebe). This is no issue if you test the process by itself or - for integration tests - start your app in a dedicated process.

## License

This library is developed under

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](/LICENSE)

## Sponsors and Customers

[![sponsored](https://img.shields.io/badge/sponsoredBy-Holisticon-red.svg)](https://holisticon.de/)
