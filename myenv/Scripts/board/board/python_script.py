import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from users.views import your_attendance_view_function

if __name__ == "__main__":
    your_attendance_view_function()


# Creating a MySQL trigger and stored procedure involves running SQL commands on your MySQL database. Since you mentioned you're new, here's a step-by-step guide on how to create a MySQL trigger and stored procedure:

# **Step 1: Access Your MySQL Database**

# 1. Open a command prompt or terminal and log in to your MySQL database server using a MySQL client like the following:

#    ```
#    mysql -u your_username -p
#    ```

#    Replace `your_username` with your MySQL username, and you'll be prompted to enter your password.

# **Step 2: Create a Stored Procedure**

# 2. Create a stored procedure that will execute your Python script or call your Django view function when the trigger is activated. Replace `/path/to/your/python_script.py` with the actual path to your Python script.

#    ```sql
#    DELIMITER //
#    CREATE PROCEDURE execute_attendance_update()
#    BEGIN
#      -- Call an external Python script or function here
#      -- Replace 'python_script.py' with the path to your Python script
#      SET @cmd = CONCAT('python3 /path/to/your/python_script.py');
#      -- Execute the Python script
#      SELECT sys_exec(@cmd);
#    END;
#    //
#    DELIMITER ;
#    ```

# **Step 3: Create a MySQL Trigger**

# 3. Create a MySQL trigger that will activate the stored procedure when a change occurs in your device logs table. Replace `device_logs` with the actual name of your device logs table.

#    ```sql
#    DELIMITER //
#    CREATE TRIGGER device_log_change_trigger AFTER INSERT ON device_logs
#    FOR EACH ROW
#    BEGIN
#      -- Execute the stored procedure
#      CALL execute_attendance_update();
#    END;
#    //
#    DELIMITER ;
#    ```

# **Step 4: Verify and Exit**

# 4. Verify that the stored procedure and trigger have been created successfully:

#    ```sql
#    SHOW PROCEDURE STATUS;
#    SHOW TRIGGERS;
#    ```

#    You should see your stored procedure and trigger listed.

# **Step 5: Exit MySQL**

# 5. Once you've verified that everything is set up correctly, you can exit the MySQL client:

#    ```sql
#    EXIT;
#    ```

# That's it! You've created a MySQL trigger and stored procedure that can be used to execute your Python script or Django view function when changes occur in the device logs table. Remember to replace placeholders like `your_username`, `/path/to/your/python_script.py`, and `device_logs` with your actual database and file paths.
