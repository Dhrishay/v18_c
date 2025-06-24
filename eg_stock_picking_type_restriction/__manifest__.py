{
    'name': 'Operation Type Restriction ',
    'version': '18.1',
    'category': 'Sales',
    'summary': 'Restrict user access to specific stock picking types, blocking unauthorized creation or editing of operation types for enhanced security. , Operation Type Restriction Odoo, Stock Picking Type Restriction Odoo, User Access Control Odoo, Operation Type Security Odoo, Restrict Inventory Operations Odoo, Role-Based Access Control Odoo, Operation Type Permissions Odoo, Block Unauthorized Access Odoo, Limit Operation Visibility Odoo, Operation Type Edit Restriction Odoo, Operation Type Creation Restriction Odoo, Error on Unauthorized Action Odoo, Inventory Security Odoo, Manage Operation Types Odoo, Stock Picking Type Visibility Odoo, User Group Permissions Odoo, Admin Access Control Odoo, Operation Management Odoo, Secure Inventory Operations Odoo, Block Unauthorized Operation Creation Odoo. stock picking type restriction, restrict stock operations, warehouse access control, stock transfer limitations, inventory movement restrictions, stock picking user permissions, warehouse operation security, controlled stock transfers, limit stock actions by user, stock management access control, advanced inventory restrictions, picking type access rights, warehouse role-based restrictions, Odoo stock picking restrictions, Odoo warehouse access control, Odoo inventory movement control, Odoo stock transfer permissions, Odoo warehouse security settings, Odoo stock operation customization, Odoo controlled inventory transfers, Odoo picking type role management.',
    'description': """
        The Operation Type Restriction app enhances security by controlling which users can view, create, or edit specific stock picking types. Administrators can apply role-based access restrictions, ensuring that only authorized personnel have access to sensitive inventory operations.

        Key Features:
        1) Operation Type Access Restriction:
           - Allows administrators to set access restrictions on operation types per user, limiting visibility and actions to authorized personnel only.

        2) Creation & Editing Permissions:
           - Provides specific group permissions to restrict users from creating or editing operation types, ensuring that only authorized users manage these settings.

        3) Error Notification for Unauthorized Actions:
           - Users attempting unauthorized actions receive clear error messages, preventing accidental or unauthorized access.
    """,
    'author': 'INKERP',
    'website': "http://www.inkerp.com",
    'depends': ['stock', 'sale_management'],
    'data': [
        'security/group.xml',
        'views/res_users_view.xml'

    ],
    'images': ['static/description/banner.gif'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '15.00',
    'currency': 'EUR',
}
