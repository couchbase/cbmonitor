Feature: Home page

    Scenario: Accessing home page
        Given I access the url "/"
        Then I get status code 404
