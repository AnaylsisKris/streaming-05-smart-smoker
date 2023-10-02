"""
    Smoker Temperature Monitoring during cooking via "smart smoker"
    This program listens for Food B messages contiously. 
    If smoker temp decreases by 15 F or more in 2.5 min (or 5 readings)  --> smoker alert!

    Author: Kristen Finley
    Date: September 27, 2023

"""
# Imports
import pika
import sys
from datetime import datetime
from collections import deque

# send email alerts (unable to set up tomllib)
# requires emailer.py file
# from emailer import createAndSendEmailAlert
#import tomllib  # requires Python 3.11
#import pprint
#from email.message import EmailMessage
#import smtplib

# At one reading every 1/2 minute, the smoker deque max length is 5 (2.5 min * 1 reading/0.5 min)
temp_deque = deque(maxlen=6)
time_deque = deque(maxlen=6)

# Configure logging
from util_logger import setup_logger
logger, logname = setup_logger(__file__)


# Define functions

# define a callback function to be called when a message is received
def smoker_callback(ch, method, properties, body):
    """ Define behavior on getting a message about the smoker temperature."""
    #decode bindary message as a string
    logger.info(f"[x] Received Message:{body.decode()}")


    try:
        #replace empty values with None
        original_message = body.decode().split(",")
        message = list(map(lambda x: x if x is not ' ' else None, original_message))

        #convert date and time from string to datetime obj
        dt_format = '%m/%d/%y %H:%M:%S'
        time_obj = datetime.strptime(message[0], dt_format) 

        # process messages without values
        if message[1] == None:
            logger.info(f"[x] Processed. No food temp recorded at {time_obj}")
            logger.info("----------------------------------------")


        # process messages with values
        elif message[1]:

            # initialize array for temp
            temp = [0]
            # convert temp array to float
            temp[0] = round(float(message[1]),1)
            # insert value on the right side of the deque
            temp_deque.append(temp[0])
            filter(lambda x: x!=None, temp_deque)
            # calculate temp change of deque
            temp_change = (temp_deque[-1] - temp_deque[0])


            # initialize array for time
            time_array = [time_obj]
            # inserts value on the right side of deque
            time_deque.append(time_array[0])
            # calculate time change of deque
            time_previous = time_deque[0]
            time_current = time_deque[-1]
            time_change = (time_current - time_previous)

            logger.info(f"[x] Processed. Temperature Change: {round(float(temp_change),1)} degrees. Time Change: {time_change} mins.")
            logger.info("----------------------------------------")

            # using deque, create the alert for temps > 15 deg every 6 readings
            if len(temp_deque) == 6:

                if temp_change < -15.0:
                    logger.info("----------------------------------------")
                    logger.info(f"SMOKER ALERT! --> smoker temp decreases by 15.0 degF or more in 2.5 min (or 6 readings)")
                    logger.info(f"Temperature Change: {round(float(temp_change),1)} degF. Time Change: {time_change} mins.")
                    logger.info("----------------------------------------")

                    # send email alerts (not set up)
                    '''
                    email_subject = "SMOKER ALERT!"
                    email_body = (f"Temperature Change: {round(float(temp_change),1)} degrees. Time Change: {time_change} mins.")
                    createAndSendEmailAlert(email_subject, email_body)
                    '''

        # (now it can be deleted from the queue)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error("An error has occurred with the message.")
        logger.error(f"The error says: {e}.")
        SystemExit



# define a main function to continuously listen for task messages on named queue
def main(hn: str = "localhost", qn: str = "queue_name"):

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        print()
        logger.error("ERROR: connection to RabbitMQ server failed.")
        logger.error(f"Verify the server is running on host={hn}.")
        logger.error(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # use the connection to create a communication channel
        ch = conn.channel()

        # use the channel to queue_delete() each queue
        # ch.queue_delete(queue=qn)

        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=qn, durable=True)

        # The QoS level controls the # of messages
        # that can be in-flight (unacknowledged by the consumer)
        # at any given time.
        # Set the prefetch count to one to limit the number of messages 
        # being consumed and processed concurrently.
        # This helps prevent a worker from becoming overwhelmed
        # and improve the overall system performance. 
        # prefetch_count = Per consumer limit of unaknowledged messages      
        ch.basic_qos(prefetch_count=1) 


        # Use the call to configure the channel to listen to a named queue 
        # and assign a callback function 
        # use the callback function named smoker_callback,
        # and do not auto-acknowledge the message (let the callback handle it)
        ch.basic_consume(
            queue=qn, on_message_callback=smoker_callback, auto_ack=False
        )

        # print a message to the console for the user
        logger.info("[x] Ready for work. To exit press CTRL+C")
        logger.info("----------------------------------------")


        # start consuming messages via the communication channel
        ch.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        print()
        logger.error("ERROR: something went wrong.")
        logger.error(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        logger.info(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        logger.info("\nClosing connection. Goodbye.\n")
        ch.queue_delete(qn)
        conn.close()


# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    # call the main function with the information needed
    main("localhost", "01-smoker")