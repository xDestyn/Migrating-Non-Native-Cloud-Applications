import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                msg.get_body().decode('utf-8'))

    notification_id = int(msg.get_body().decode('utf-8'))
    connection = None
    attendees = None
    notification_count = 0

    try:
        # Connecting to server
        connection = connect_database()
        
        # Allows Python code to execute PostgreSQL command in a database session
        cursor = connection.cursor()
        
        # TODO: Get notification message and subject from database using the notification_id
        logging.info('Type of notification_id: %s', type(notification_id))
        notification = get_notification_by_id(notification_id, cursor)
        
        logging.info('Notification fetched: %s', notification)

        # TODO: Get attendees email and name
        attendees = get_attendees(cursor)
        
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            logging.info(f'Sending email to: {attendee.first_name} {attendee.last_name}')
            # subject = '{first_name}: {subject}'.format(attendee.first_name, notification.subject)
            # logging.info(f'Subject {subject}')
            notification_count += send_email(attendee.email, notification.subject, notification.message)
        
        logging.info(f'Notified {notification_count} attendees')
            
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        update_notification_table(connection, cursor, notification_id, notification_count, datetime.today())
        

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        if connection is not None:
            connection.close()
            logging.info('Closed connection')


### --- Functions ---###
"""
Returns:
    _type_: PostgreSQL connection
"""        
def connect_database():
    connection = None
    try:
        logging.info('Connecting to PostgreSQL database...')
        # Connecting to server
        connection = psycopg2.connect(host='udacity-proj3-server.postgres.database.azure.com',
                                    database='techconfdb',
                                    user='xdestyn@udacity-proj3-server',
                                    password='ComplexEntity14!' )
        
    except(Exception, psycopg2.DatabaseError) as error:
        logging.eror(error)
            
    return connection

"""
Parameters:
    notification_id: Message context
    cursor: PostgreSQL cursor
Returns:
    _type_: 
"""
def get_notification_by_id(notification_id, cursor):
    logging.info('Get notification by id: %s', str(notification_id))
    # PostgreSQL query
    cursor.execute("SELECT MESSAGE, SUBJECT FROM NOTIFICATION WHERE ID = %s;", [notification_id])
    # Get row
    row = cursor.fetchone()
    notification = Notification(row[0], row[1])
    
    return notification
    
"""
Parameter:
    cursor: PostgreSQL cursor
Returns:
    _type_: Array of attendees fetched from PostgreSQL database
"""
def get_attendees(cursor):
    # PostgreSQL query
    cursor.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL FROM ATTENDEE;")
    # Get all rows 
    rows = cursor.fetchall()
    # Attendee containers
    attendees = []
    # Loop through returned query output and store new instance of Attendee
    for row in rows:
        attendee = Attendee(row[0], row[1], row[2])
        attendees.append(attendee)
        
    return attendees

"""
Parameter: 
    email: Email recipient
    subject: Email subject
    body: Email body
Returns: 
    _type_: 0 or 1 as failure or successful respectively
"""
def send_email(email, subject, message):
    # Get send grip api key from environment variables
    send_grid_api_key = "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"
    
    # Successful sent notifications
    count = 0
    
    if send_grid_api_key:
        try:
            # Create email object
            email_message = Mail(from_email='omarflores2021@outlook.com',
                                to_emails=email,
                                subject=subject,
                                plain_text_content=message)
            # Initiate send grid client
            send_grid_client = SendGridAPIClient(send_grid_api_key)
            # Send email
            send_grid_client.send(email_message)
            logging.info(f'Email: {email} has been sent.')
            count+=1
        except Exception as exception:
            logging.error(exception)
        
    return count

"""
Parameter:
    connection: PostgreSQL database connection
    cursor: PostgreSQL cursor
    notification_id: Message context
    notification_count: Successful notified attendees
    completed_date: Date updated was completed 
"""
def update_notification_table(connection, cursor, notification_id, notification_count, completed_date):
    # PostgreSQL query
    cursor.execute("UPDATE NOTIFICATION SET STATUS = %s, COMPLETED_DATE = %s WHERE ID = %s;", (notification_count, completed_date, notification_id,))
    # Commit transaction
    connection.commit()
    
    logging.info('Update successful')

###--- Classes ---### 
class Attendee(object):
    def __init__(self, f_name, l_name, email):
        self.first_name = f_name
        self.last_name = l_name
        self.email = email
        
    def __str__(self):
        return f'Attendee Information: {self.last_name}, {self.first_name}, {self.email}'
    
class Notification(object):
    def __init__(self, msg, sub):
        self.message = msg
        self.subject = sub

    def __str__(self):
        return f'Notification: {self.message}, {self.subject}'
