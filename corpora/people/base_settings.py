# -*- coding: utf-8 -*-

# This is a fixed UUID so that we can reference a person when requied
# e.g. when a Machine creates a QualityControl it needs a person object.
# Perhaps if we try to create a QC without a person, we should throw
# an error or give it a default person?
MACHINE_PERSON_UUID = "dc9de72c-65bc-4d8e-b2bb-c53b85d1b712"
