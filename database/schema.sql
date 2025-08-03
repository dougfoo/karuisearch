-- Karui-Search Database Schema
-- SQLite compatible with PostgreSQL extensions

-- Enable foreign key constraints (SQLite)
PRAGMA foreign_keys = ON;

-- Sources table: Track different real estate websites
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1, -- requests per second
    last_scraped TIMESTAMP,
    success_rate DECIMAL(5,2) DEFAULT 100.0,
    total_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property types enum (handled as check constraint)
CREATE TABLE property_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    name_japanese VARCHAR(50),
    description TEXT
);

-- Insert default property types
INSERT INTO property_types (name, name_japanese, description) VALUES 
('house', '一戸建て', 'Single-family house'),
('apartment', 'マンション', 'Apartment or condominium'),
('land', '土地', 'Land plot'),
('vacation_home', '別荘', 'Vacation or resort home');

-- Properties table: Simplified for V1
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Essential fields (V1)
    title VARCHAR(500) NOT NULL,
    price VARCHAR(100) NOT NULL,           -- keep original format
    location VARCHAR(500) NOT NULL,        -- address/area as displayed
    property_type VARCHAR(50),             -- house/apartment/land as shown
    size_info VARCHAR(200),                -- sizes as displayed on site
    building_age VARCHAR(100),             -- age as displayed on site
    source_url VARCHAR(1000) NOT NULL,
    scraped_date DATE NOT NULL,
    
    -- Optional fields (V1)
    description TEXT,
    image_urls TEXT,                       -- JSON array of image URLs (max 5)
    rooms VARCHAR(50),                     -- layout like "3LDK"
    
    -- Source tracking
    source_id INTEGER REFERENCES sources(id),
    source_property_id VARCHAR(100),       -- original ID from source site
    
    -- Status tracking
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    date_first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_scraped_date CHECK (scraped_date IS NOT NULL),
    CONSTRAINT valid_source_url CHECK (length(source_url) > 0)
);

-- Property images table
CREATE TABLE property_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    original_url VARCHAR(1000) NOT NULL,
    local_path VARCHAR(500), -- local file path if downloaded
    image_type VARCHAR(50), -- main, exterior, interior, floor_plan, etc.
    width INTEGER,
    height INTEGER,
    file_size INTEGER, -- bytes
    alt_text VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property history: Track price and status changes
CREATE TABLE property_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL, -- price, status, etc.
    old_value TEXT,
    new_value TEXT,
    change_type VARCHAR(50), -- created, updated, deleted
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraping jobs: Track scraping activities
CREATE TABLE scraping_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    job_type VARCHAR(50) NOT NULL, -- full, incremental, retry
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    properties_found INTEGER DEFAULT 0,
    properties_new INTEGER DEFAULT 0,
    properties_updated INTEGER DEFAULT 0,
    properties_removed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_details TEXT, -- JSON array of errors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly reports: Track generated reports
CREATE TABLE weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    properties_count INTEGER DEFAULT 0,
    new_properties_count INTEGER DEFAULT 0,
    report_format VARCHAR(20), -- html, json, pdf
    file_path VARCHAR(500),
    file_size INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_week_dates CHECK (week_end_date >= week_start_date)
);

-- Report properties: Link properties to reports
CREATE TABLE report_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER REFERENCES weekly_reports(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    inclusion_reason VARCHAR(100), -- new, price_change, featured
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(report_id, property_id)
);

-- Duplicate candidates: Track potential duplicates
CREATE TABLE duplicate_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property1_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    property2_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    similarity_score DECIMAL(5, 4), -- 0.0000 to 1.0000
    matching_fields TEXT, -- JSON array of matching fields
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, dismissed
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT different_properties CHECK (property1_id != property2_id),
    CONSTRAINT valid_similarity CHECK (similarity_score >= 0.0 AND similarity_score <= 1.0)
);

-- Search filters: Save user search preferences
CREATE TABLE saved_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    filters TEXT NOT NULL, -- JSON object with search criteria
    email_notifications BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_properties_source ON properties(source_id);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_location ON properties(city, prefecture);
CREATE INDEX idx_properties_type ON properties(property_type_id);
CREATE INDEX idx_properties_date_seen ON properties(date_first_seen);
CREATE INDEX idx_properties_active ON properties(is_active);
CREATE INDEX idx_properties_source_url ON properties(source_url);

CREATE INDEX idx_property_images_property ON property_images(property_id);
CREATE INDEX idx_property_images_primary ON property_images(property_id, is_primary);

CREATE INDEX idx_property_history_property ON property_history(property_id);
CREATE INDEX idx_property_history_date ON property_history(changed_at);

CREATE INDEX idx_scraping_jobs_source ON scraping_jobs(source_id);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_date ON scraping_jobs(created_at);

CREATE INDEX idx_weekly_reports_date ON weekly_reports(week_start_date, week_end_date);

CREATE INDEX idx_duplicate_candidates_property1 ON duplicate_candidates(property1_id);
CREATE INDEX idx_duplicate_candidates_property2 ON duplicate_candidates(property2_id);
CREATE INDEX idx_duplicate_candidates_similarity ON duplicate_candidates(similarity_score);

-- Create views for common queries
CREATE VIEW active_properties AS
SELECT 
    p.*,
    pt.name as property_type_name,
    pt.name_japanese as property_type_japanese,
    s.name as source_name
FROM properties p
JOIN property_types pt ON p.property_type_id = pt.id
JOIN sources s ON p.source_id = s.id
WHERE p.is_active = TRUE AND p.is_sold = FALSE;

CREATE VIEW property_summary AS
SELECT 
    p.id,
    p.title,
    p.price,
    p.land_area,
    p.building_area,
    p.address,
    p.rooms,
    pt.name as property_type,
    s.name as source,
    p.date_first_seen,
    COUNT(pi.id) as image_count
FROM properties p
JOIN property_types pt ON p.property_type_id = pt.id
JOIN sources s ON p.source_id = s.id
LEFT JOIN property_images pi ON p.id = pi.property_id
WHERE p.is_active = TRUE
GROUP BY p.id, p.title, p.price, p.land_area, p.building_area, 
         p.address, p.rooms, pt.name, s.name, p.date_first_seen;

-- Insert default sources
INSERT INTO sources (name, base_url, rate_limit) VALUES 
('SUUMO', 'https://suumo.jp', 2),
('At Home', 'https://www.athome.co.jp', 1),
('Homes.co.jp', 'https://www.homes.co.jp', 2);

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_properties_timestamp 
AFTER UPDATE ON properties
BEGIN
    UPDATE properties SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_sources_timestamp 
AFTER UPDATE ON sources
BEGIN
    UPDATE sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create trigger for property history tracking
CREATE TRIGGER track_property_changes
AFTER UPDATE ON properties
FOR EACH ROW
WHEN OLD.price != NEW.price OR OLD.is_active != NEW.is_active OR OLD.is_sold != NEW.is_sold
BEGIN
    INSERT INTO property_history (property_id, field_name, old_value, new_value, change_type)
    VALUES 
    (NEW.id, 
     CASE 
         WHEN OLD.price != NEW.price THEN 'price'
         WHEN OLD.is_active != NEW.is_active THEN 'is_active'
         WHEN OLD.is_sold != NEW.is_sold THEN 'is_sold'
     END,
     CASE 
         WHEN OLD.price != NEW.price THEN CAST(OLD.price AS TEXT)
         WHEN OLD.is_active != NEW.is_active THEN CAST(OLD.is_active AS TEXT)
         WHEN OLD.is_sold != NEW.is_sold THEN CAST(OLD.is_sold AS TEXT)
     END,
     CASE 
         WHEN OLD.price != NEW.price THEN CAST(NEW.price AS TEXT)
         WHEN OLD.is_active != NEW.is_active THEN CAST(NEW.is_active AS TEXT)
         WHEN OLD.is_sold != NEW.is_sold THEN CAST(NEW.is_sold AS TEXT)
     END,
     'updated');
END;