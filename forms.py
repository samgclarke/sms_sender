from wtforms import Form, IntegerField, TextField, validators


class SMSForm(Form):
    #number = IntegerField('Phone Number', [validators.Length(min=4, max=25)])
    #message = TextField('Message', [validators.Length(min=6, max=144)])
    number = TextField('Phone Number')
    message = TextField('Message')
