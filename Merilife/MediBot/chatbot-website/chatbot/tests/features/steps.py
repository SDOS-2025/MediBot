from behave import *
from chatbot.models import CustomUser, Report

@given('a patient with symptoms "{symptoms}"')
def create_patient(context, symptoms):
    context.patient = CustomUser.objects.create(
        role='PATIENT',
        symptoms=symptoms
    )

@when('they complete screening with duration "{duration}"')
def complete_screening(context, duration):
    # Simulate chat interaction
    context.execute_steps(f'''
        When they enter "{duration}" for duration
        And answer "no" to other symptoms
    ''')

@then('a report with "{diagnosis}" diagnosis should be generated')
def verify_report(context, diagnosis):
    report = Report.objects.get(patient=context.patient)
    assert diagnosis in report.content