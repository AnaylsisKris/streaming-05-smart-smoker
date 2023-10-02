# streaming-05-smart-smoker (continued)

- Class: STREAMING DATA 44671-80/81FA23
- Assignment: P6-- Guided Programming: Consumers, Windowing, and Multiple Channels
- Name: Kristen Finley
- Date: September 27, 2023

---
## Task 1. Open Your Existing Project
1.	On your machine, open your existing streaming-05-getting-started repo in VS Code.
2.	Create a file for your consumer (or 3 files if you'd like to use 3 consumers).
 
## Task 2. Design and Implement Each Consumer
1.	Design and implement each bbq consumer. You could have one. You could have 3.  More detailed help provided in links below. 
2.	Use the logic, approach, and structure from prior modules (use the recommended versions).
3.	Modifying them to serve your purpose IS part of the assignment.
4.	Do not start from scratch - do not search for code - do not use a notebook.
5.	Use comments in the code and repo to explain your work. 
6.	Use docstring comments and add your name and date to your README and your code files. 
 
## Task 3. Professionally Present your Project
1.	Explain your project in the README.
2.	Include your name, date.
3.	Include prerequisites and how to run your code. 
4.	Explain and show how your project works. 
5.	Tell us what commands are needed. Use code fencing in GitHub or backtics for inline code to share commands.
6.	Display screenshots of your console with the producer and consumer running.
7.	Display screenshots of at least one interesting part of the RabbitMQ console. 
 ---
# Module 6.1: Guided Consumer Design
## Consumer Design
Many things are are the same for each consumer. The first question is:
1.	Do you want 3 different consumers? Or do you want one consumer that listens to all 3 queues? Either works. 
2.	If you do 3 different consumers, each is very similar to what we've done before.
 
## Designing Each Consumer
1.	How many connections do you need? Hint: Just one connection per consumer.
2.	Create a connection object. 
3.	How many communication channels do you need? Hint: Just one communication channel per consumer.
4.	How many queues do you need: Hint: see the queue names in the problem description. How many queue names are there?
5.	Call channel.queue_declare() once for each queue.
6.	Provide the appropriate arguments as you've done before - see prior examples.
7.	Declare different callback functions
    1.	smoker_callback(),
    2.	foodA_callback(),
    3.	foodB_callback()
8.	You can have one per consumer, or three if you're implementing a single consumer.
9.	Each callback has the same signature and general approach as you've seen before.
10.	More about each callback later - for now, just "stub it in" and we'll come back to finish the callbacks later. 
11.	This is common - we build code more like an outline - from the outside in.
12.	We don't write code from left to right like an essay.  Just make a callback that doesn't kill your program - defer the logic until later.
13.	Set up a basic consume once for each queue. 
    1.	Call channel.basic_consume() once for each queue.
    2.	Follow prior examples.
    3.	set auto_ack to False - we've explored both options, but we want to process the message first, before we acknowledge it and have it removed from the queue. 
    4.	set on_message_callback to the name of the callback function.
    5.	Important: assigning the function does NOT include the parenthesis.
    6.	If you add parenthesis after the name, you'll accidentally CALL the function instead of assigning it (don't do this).
14.	Call channel.start_listening() just once - the configured communication channel will listen on all three configured queues.

---
# Module 6.2: Guided Consumer Implementation
## Consumer Implementation Questions/Remarks
1.	Will you use a file docstring at the top?
    - yes
2.	Where do imports go?
    - right after the file/module docstring
3.	After imports, declare any constants. 
4.	After constants, define functions - define your callback function(s) here.
5.	Use the examples to create each callback. It'll have the same arguments. For now, just have a callback function:
    1.	acknowledge the message was received and processed
6.	Define a main() function to continuously listen for task messages on a named queue.
7.	In this main() function:
    1.	create a blocking connection to the RabbitMQ server
    2.	use the connection to create a communication channel
    3.	use the channel to queue_delete() each queue
    4.	use the channel to queue_declare() each queue
    5.	use channel.basic_consume() once for each queue. Use the call to configure the channel to listen to a named queue and assign a callback function
    6.	print a message to the console for the user that it's ready to begin (and maybe, how to exit the long-running process).
    7.	finally, use channel.start_consuming() to start consuming messages via the communication channel
    8.	Use the Python idiom to only call  your main() function only if this is actually the program being executed (not imported). 
    9.	If this is the program that was called:
1.	call your main() function, passing in just the host name as an argument, and the name of each queue this consumer monitors
 
# Module 6.3: Implementing a Callback Function
## Callbacks
Each listening queue has its own callback function, providing the logic for how to process a message on getting one from that queue.
 
## Consumer Pattern is Very Standard
Outside of the callbacks, each consumer tends to be very similar - this is good. In software, we don't express ourselves by re-writing or re-wording things that work. A general consumer, well-written, can by widely reused. The custom analytics and/or processing is done in the callback function - these are critical. We'll look at the callback function assigned to the smoker queue - apply similar logic to create the callbacks for Food A and Food B.
 
## Start Simple
Earlier, we asked you to stub in a callback, by ignoring all the logic and skipping to the acknowledgement. 
When not using auto-acknowledge (auto_ack = False), your smoker_callback() might look like this:

```
# define a callback function to be called when a message is received
def smoker_callback(ch, method, properties, body):
    """ Define behavior on getting a message about the smoker temperature."""
    # decode the binary message body to a string
    print(f" [x] Received {body.decode()}")
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)
```
It works, doesn't kill your program and allows you to write the main parts of your consumer from earlier examples. 
How would this change if auto_ack was True?
 
## Smart Smoker Consumer Data Challenges
If you look at the data carefully, you'll notice that we don't get our temperature readings on a regular basis. 
•	The timestamps are offset, and many intervals have missing data. 
•	In the real world, this is why analysts can earn good money - nothing is ever as easy as it looks. 
•	For school, we will make some simplifying assumptions and focus on the overall process. 
 
## Simplifying assumptions
For class, assume each data point with a value occurs on a regular basis and add it to the deque. 
That is: 
- IGNORE the real timestamps
- evaluate the deque of readings (either 5 or 20) as though the real timestamps were not so terrible.

It's more complex if we try to use real timestamps. Adjusting for the non-regular timestamps is an interesting problem, but not the point. Know that you will likely have to address issues like that in the "real world". 
