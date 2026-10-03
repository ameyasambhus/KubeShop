-- ==============================================================================
-- KubeShop PostgreSQL Multi-Database Initialization
-- ==============================================================================
-- In Docker Compose, a single PostgreSQL instance hosts two isolated databases
-- to simulate distinct microservice data ownership without excessive memory usage.
-- ==============================================================================

CREATE DATABASE kubeshop_product;
CREATE DATABASE kubeshop_order;

-- Grant permissions to default postgres user
GRANT ALL PRIVILEGES ON DATABASE kubeshop_product TO postgres;
GRANT ALL PRIVILEGES ON DATABASE kubeshop_order TO postgres;
