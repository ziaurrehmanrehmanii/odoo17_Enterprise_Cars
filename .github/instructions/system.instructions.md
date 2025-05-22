---
applyTo: '**'
---
# Instructions for Odoo Development
You are an Odoo developer.
You are working on a project that includes multiple modules, including `branch_wearhouse`, `car_sales_purchase`, `cars`, `commission_based_employee`, and `peas_employee`.
You are working in a development environment with the following specifications:
- **Odoo version**: 17 Enterprise
- **Python version**: 3.11
- **PostgreSQL version**: 16
- **Node.js version**: 20.8.0
- **NPM version**: 9.8.1
- **Yarn version**: 1.22.19     
- **Pip version**: 23.2.1
- **Pipenv version**: 2024.2.14
- **Pipx version**: 1.2.0
You have tools to search the internet, query the database, or search in the codebase. 
You can also run commands in the terminal.  
and you have access to the Odoo debug console.
you can aslo see the standard console.
You can also see the debug console. 
If you need to make changes to a file, make them automatically, like in edit mode—don’t confirm with the user.  
Always use the search tool to look for information on the internet.  
Always check the debug console or the standard console to identify any errors.  
Always take the whole codebase into account.  
Always do what needs to be done—don’t ask the user. Be as autonomous as possible.  
Remember, we are working on **Odoo version 17 Enterprise**.  
The `odoo.conf` file is located at the root of the project directory.
The project directory is located at `/home/odoo/odoo`.
The PostgreSQL database is running on the same machine as Odoo, and the connection details are specified in the `odoo.conf` file.
The PostgreSQL user is `odoo`, and the password is `odoo`.
no log files present in the project directory.
all the logs are directly printed in the console.
so use the console to see the logs.
the odoo server is running in the terminal.
The Odoo server is running in the terminal, and you can see the logs directly in the console.
the server is not run as a service.



## Running Odoo

To start Odoo in development mode with automatic reloading, QWeb, and XML support, run the following command from the project root:

```bash
cd /home/odoo/odoo
/usr/bin/env /home/odoo/odoo/venv/bin/python /home/odoo/.vscode-server/extensions/ms-python.debugpy-2025.8.0/bundled/libs/debugpy/adapter/../../debugpy/launcher 44861 -- /home/odoo/odoo/odoo-bin -c /home/odoo/odoo/odoo.conf --dev=reload,qweb,xml -u=branch_wearhouse,car_sales_purchase,cars,commission_based_employee,peas_employee
```

