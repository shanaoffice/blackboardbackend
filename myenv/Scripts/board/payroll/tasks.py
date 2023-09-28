from background_task import background

@background(schedule=30)  # This is just a placeholder schedule; it will be overridden by the crontab.
def my_monthly_task():
    # Your task logic here
    print("Hello, this is my monthly task.")
