-- Questao 2 - DDL das tabelas bronze (tipos inferidos a partir dos CSVs)

CREATE TABLE bronze.addresses (
    id INTEGER,
    customer_id INTEGER,
    address_type TEXT,
    postal_code TEXT,
    street TEXT,
    number INTEGER,
    complement TEXT,
    district TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    is_primary TEXT,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.attributes (
    id TEXT,
    name TEXT,
    data_type TEXT,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.brands (
    id INTEGER,
    name TEXT,
    country TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.categories (
    id INTEGER,
    name TEXT,
    slug TEXT,
    parent_category_id TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.customers (
    id INTEGER,
    person_type TEXT,
    legal_name TEXT,
    trade_name TEXT,
    tax_id TEXT,
    state_registration TEXT,
    email TEXT,
    phone TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.employees (
    id INTEGER,
    full_name TEXT,
    cpf TEXT,
    email TEXT,
    role TEXT,
    primary_location_id TEXT,
    hire_date DATE,
    termination_date DATE,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.fiscal_invoices (
    id INTEGER,
    order_id INTEGER,
    nfe_number TEXT,
    nfe_access_key TEXT,
    series TEXT,
    issued_at TIMESTAMP,
    status TEXT,
    total_amount NUMERIC,
    xml_storage_uri TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.goods_receipt_items (
    id INTEGER,
    goods_receipt_id INTEGER,
    purchase_order_item_id INTEGER,
    quantity_received TEXT,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.goods_receipts (
    id INTEGER,
    purchase_order_id INTEGER,
    received_by_employee_id INTEGER,
    received_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.locations (
    id TEXT,
    name TEXT,
    location_type TEXT,
    postal_code TEXT,
    street TEXT,
    number INTEGER,
    complement TEXT,
    district TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.order_items (
    id INTEGER,
    order_id INTEGER,
    product_variant_id INTEGER,
    quantity INTEGER,
    unit_price NUMERIC,
    icms_rate NUMERIC,
    ipi_rate NUMERIC,
    line_total NUMERIC,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.orders (
    id INTEGER,
    order_number TEXT,
    channel TEXT,
    customer_id INTEGER,
    salesperson_id INTEGER,
    location_id TEXT,
    status TEXT,
    subtotal NUMERIC,
    discount_amount NUMERIC,
    total NUMERIC,
    placed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.payments (
    id INTEGER,
    order_id INTEGER,
    method TEXT,
    installments INTEGER,
    amount NUMERIC,
    status TEXT,
    paid_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.product_suppliers (
    product_variant_id INTEGER,
    supplier_id INTEGER,
    supplier_sku TEXT,
    last_quoted_cost NUMERIC,
    lead_time_days INTEGER,
    is_preferred TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.product_variants (
    id INTEGER,
    product_id INTEGER,
    sku TEXT,
    barcode_ean TEXT,
    sale_price NUMERIC,
    cost_price NUMERIC,
    weight_kg TEXT,
    icms_rate NUMERIC,
    ipi_rate NUMERIC,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.products (
    id INTEGER,
    name TEXT,
    description TEXT,
    brand_id INTEGER,
    category_id INTEGER,
    ncm_code TEXT,
    unit_of_measure TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.purchase_order_items (
    id INTEGER,
    purchase_order_id INTEGER,
    product_variant_id INTEGER,
    quantity_ordered INTEGER,
    unit_cost NUMERIC,
    line_total NUMERIC,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.purchase_orders (
    id INTEGER,
    po_number TEXT,
    supplier_id INTEGER,
    buyer_id INTEGER,
    destination_location_id TEXT,
    status TEXT,
    currency TEXT,
    subtotal NUMERIC,
    total NUMERIC,
    placed_at TIMESTAMP,
    expected_delivery_at DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.return_items (
    id INTEGER,
    return_id INTEGER,
    order_item_id INTEGER,
    quantity TEXT,
    action TEXT,
    exchange_variant_id INTEGER,
    unit_refund_amount NUMERIC,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.returns (
    id INTEGER,
    return_number TEXT,
    order_id INTEGER,
    customer_id INTEGER,
    received_at_location_id TEXT,
    status TEXT,
    reason TEXT,
    total_refund_amount NUMERIC,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.stock_levels (
    product_variant_id INTEGER,
    location_id TEXT,
    quantity_on_hand NUMERIC,
    reorder_point TEXT,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.stock_movements (
    id INTEGER,
    product_variant_id INTEGER,
    location_id TEXT,
    movement_type TEXT,
    quantity TEXT,
    reference_table TEXT,
    reference_id INTEGER,
    employee_id INTEGER,
    notes TEXT,
    occurred_at TIMESTAMP,
    created_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.suppliers (
    id INTEGER,
    legal_name TEXT,
    trade_name TEXT,
    country TEXT,
    tax_id TEXT,
    tax_id_type TEXT,
    email TEXT,
    phone TEXT,
    contact_name TEXT,
    is_active TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

CREATE TABLE bronze.variant_attribute_values (
    product_variant_id INTEGER,
    attribute_id TEXT,
    value TEXT,
    _source_file TEXT,
    _loaded_at TIMESTAMP,
    _line_number INTEGER
);

