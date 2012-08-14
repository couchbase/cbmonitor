Feature: Admin module

    Scenario: Accessing login page
        Given I access the url "/admin/login/"
        Then I get status code 200
