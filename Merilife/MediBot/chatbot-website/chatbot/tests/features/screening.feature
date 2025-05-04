Feature: Patient Screening
  Scenario: Cold symptom diagnosis
    Given a patient with symptoms "cold"
    When they complete screening with duration "2 days"
    Then a report with "URI" diagnosis should be generated