class CustomDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'users' and model._meta.db_table=='devicelogs_processed' :  # Replace 'your_app_name' with the actual app name
            return 'client_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'users' and model._meta.db_table=='devicelogs_processed' :  # Replace 'your_app_name' with the actual app name
            return 'client_db'
        return 'default'