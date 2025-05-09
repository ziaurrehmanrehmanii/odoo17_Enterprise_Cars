# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dominican Republic - Accounting',
    'icon': '/account/static/description/l10n.png',
    'countries': ['do'],
    'version': '2.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """

Localization Module for Dominican Republic
===========================================

Catlogo de Cuentas e Impuestos para Repblica Dominicana, Compatible para
**Internacionalizacin** con **NIIF** y alineado a las normas y regulaciones
de la Direccin General de Impuestos Internos (**DGII**).

**Este mdulo consiste de:**

- Catlogo de Cuentas Estndar (alineado a DGII y NIIF)
- Catlogo de Impuestos con la mayora de Impuestos Preconfigurados
        - ITBIS para compras y ventas
        - Retenciones de ITBIS
        - Retenciones de ISR
        - Grupos de Impuestos y Retenciones:
                - Telecomunicaiones
                - Proveedores de Materiales de Construccin
                - Personas Fsicas Proveedoras de Servicios
        - Otros impuestos
- Secuencias Preconfiguradas para manejo de todos los NCF
        - Facturas con Valor Fiscal (para Ventas)
        - Facturas para Consumidores Finales
        - Notas de Dbito y Crdito
        - Registro de Proveedores Informales
        - Registro de Ingreso nico
        - Registro de Gastos Menores
        - Gubernamentales
- Posiciones Fiscales para automatizacin de impuestos y retenciones
        - Cambios de Impuestos a Exenciones (Ej. Ventas al Estado)
        - Cambios de Impuestos a Retenciones (Ej. Compra Servicios al Exterior)
        - Entre otros

**Nota:**
Esta localizacin, aunque posee las secuencias para NCF, las mismas no pueden
ser utilizadas sin la instalacin de mdulos de terceros o desarrollo
adicional.

Estructura de Codificacin del Catlogo de Cuentas:
===================================================

**Un dgito** representa la categora/tipo de cuenta del del estado financiero.
**1** - Activo        **4** - Cuentas de Ingresos y Ganancias
**2** - Pasivo        **5** - Costos, Gastos y Prdidas
**3** - Capital       **6** - Cuentas Liquidadoras de Resultados

**Dos dgitos** representan los rubros de agrupacin:
11- Activo Corriente
21- Pasivo Corriente
31- Capital Contable

**Cuatro dgitos** se asignan a las cuentas de mayor: cuentas de primer orden
1101- Efectivo y Equivalentes de Efectivo
2101- Cuentas y Documentos por pagar
3101- Capital Social

**Seis dgitos** se asignan a las sub-cuentas: cuentas de segundo orden
110101 - Caja
210101 - Proveedores locales

**Ocho dgitos** son para las cuentas de tercer orden (las visualizadas
en Odoo):
1101- Efectivo y Equivalentes
110101- Caja
11010101 Caja General
    """,
    'author': 'Gustavo Valverde - iterativo | Consultores de Odoo (http://iterativo.do)',
    'website': 'https://www.odoo.com/documentation/17.0/applications/finance/fiscal_localizations.html',
    'depends': [
        'account',
        'base_iban',
    ],
    'data': [
        'data/account_tax_report_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
