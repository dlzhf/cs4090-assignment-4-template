Feature: Task management

  Scenario: Adding a new task
    Given I start with no tasks
    When I add a task titled "Test Task"
    Then I should have exactly 1 task titled "Test Task"

  Scenario: Deleting a task
    Given I have a task titled "DeleteMe"
    When I delete the task titled "DeleteMe"
    Then I should have no tasks

  Scenario: Completing a task
    Given I have a task titled "DoMe"
    When I mark the task titled "DoMe" as completed
    Then the task titled "DoMe" should be marked completed

  Scenario: Filtering by priority
    Given I have tasks titled "A" with priority "High" and "B" with priority "Low"
    When I filter tasks by priority "High"
    Then I should only see the task titled "A"

  Scenario: Searching tasks
    Given I have tasks titled "FindMe" and "Other"
    When I search for "FindMe"
    Then I should only see the task titled "FindMe"
