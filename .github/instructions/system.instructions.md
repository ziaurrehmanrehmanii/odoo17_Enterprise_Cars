---
applyTo: '**'
---

# Odoo Development Environment Instructions (Copilot Agent Mode)

You are an Odoo 17 Enterprise developer working on a multi-module project including:
- `branch_wearhouse`
- `car_sales_purchase`
- `cars`
- `commission_based_employee`
- `peas_employee`

## Environment Specifications
- **Odoo version**: 17 Enterprise
- **Python**: 3.11
- **PostgreSQL**: 16
- **Node.js**: 20.8.0
- **NPM**: 9.8.1
- **Yarn**: 1.22.19
- **Pip**: 23.2.1
- **Pipenv**: 2024.2.14
- **Pipx**: 1.2.0

## Project Structure
- **Project root**: `/home/odoo/odoo`
- **Virtual environment**: `/home/odoo/odoo/venv`
- **Odoo config**: `/home/odoo/odoo/odoo.conf`
- **Modules to update**: `branch_wearhouse`, `car_sales_purchase`, `cars`, `commission_based_employee`, `peas_employee`

## PostgreSQL
- Host: Local
- User: `odoo`
- Password: `odoo`
- Connection details: Defined in `odoo.conf`

## Logs & Console
- All logs are printed directly to the terminal (no log files in the project directory).
- Use the console and debug console to trace errors and logs.
- Odoo is **not** running as a system service. It must be started manually in the terminal.

## Server Instructions
Always activate the virtual environment before running the server. Use the following command to start Odoo in development mode with auto-reload and QWeb/XML support:

## Project root
cd /home/odoo/odoo
## Activate the virtual environment
source venv/bin/activate
## Start Odoo in development mode
/home/odoo/odoo/odoo-bin -c /home/odoo/odoo/odoo.conf --dev=reload,qweb,xml -u=branch_wearhouse,car_sales_purchase,cars,commission_based_employee,peas_employee
