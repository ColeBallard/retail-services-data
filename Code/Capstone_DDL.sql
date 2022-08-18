drop table if exists SalesTable;
GO
drop table if exists Sales_by_categoryTable;
GO
drop table if exists NAICS_NAPCS;
GO
drop table if exists MacroTable;
GO
drop table if exists NAPCSTable;
GO
drop table if exists NAICSTable;
GO
drop table if exists DateTable;
GO

CREATE TABLE DateTable (
    DateID int PRIMARY KEY IDENTITY(1,1),
    [Year] INT,
    [Month] INT, 
);

CREATE TABLE MacroTable(
    MacroID INT PRIMARY KEY IDENTITY(1,1),
    DateID INT NOT NULL,
    CPI DECIMAL(18,10),
    RPI DECIMAL(18,10),
    USTRADE DECIMAL(18,10),
    USWTRADE DECIMAL(18,10),
    CONSTRAINT fk_MacroTable_DateID
        FOREIGN KEY (DateID)
        REFERENCES DateTable(DateID)
);

CREATE TABLE NAICSTable (
    NAICSID INT PRIMARY KEY IDENTITY(1,1),
    [2017 NAICS code (NAICS2017)] BIGINT,
    [Meaning of NAICS code (NAICS2017_LABEL)] VARCHAR(200)
);

CREATE TABLE SalesTable (
    SalesID INT PRIMARY KEY IDENTITY(1,1),
    DateID INT,
    NAICSID INT,
    [Unadjusted Sales] DECIMAL (18,4),
    [Adjusted Sales] DECIMAL (18,4),
    CONSTRAINT fk_SalesTable_NAICSID
        FOREIGN KEY (NAICSID)
        REFERENCES NAICSTable(NAICSID), 
    CONSTRAINT fk_SalesTable_DateID
        FOREIGN KEY (DateID)
        REFERENCES DateTable(DateID),
);

CREATE TABLE NAPCSTable (
    NAPCSID INT PRIMARY KEY IDENTITY(1,1),
    [2017 NAPCS collection code (NAPCS2017)] BIGINT,
    [Meaning of NAPCS collection code (NAPCS2017_LABEL)] VARCHAR(250)
);

CREATE TABLE NAICS_NAPCS (
    NAICSID INT,
    NAPCSID INT,
    [Number of establishments (ESTAB)] INT,
    [Sales, value of shipments, or revenue of NAPCS collection code ($1,000) (NAPCSDOL)] INT,
    PRIMARY KEY (NAICSID, NAPCSID),
    CONSTRAINT fk_NAISC_NAPCS_NAICSID
        FOREIGN KEY (NAICSID)
        REFERENCES NAICSTable(NAICSID),
    CONSTRAINT fk_NAISC_NAPCS_NAPCSID
        FOREIGN KEY (NAPCSID)
        REFERENCES NAPCSTable(NAPCSID)
);

CREATE TABLE Sales_by_categoryTable (
    Sales_by_categoryID INT PRIMARY KEY IDENTITY(1,1),
    DateID INT,
    [Retail sales, total] decimal(18,2),
    [Motor vehicle and parts dealers] decimal(18,2),
    [Automotive parts, acc., and tire stores] decimal(18,2),
    [Furniture and home furnishings stores] decimal(18,2),
    [Electronics and appliance stores] decimal(18,2),
    [Building mat. and garden equip. and supplies dealers] decimal(18,2),
    [Building mat. and supplies dealers] decimal(18,2),
    [Food and beverage stores] decimal(18,2),
    [Grocery stores] decimal(18,2),
    [Beer, wine and liquor stores] decimal(18,2),
    [Health and personal care stores] decimal(18,2),
    [Pharmacies and drug stores] decimal(18,2),
    [Gasoline stations] decimal(18,2),
    [Clothing and clothing access. stores] decimal(18,2),
    [Clothing stores] decimal(18,2),
    [Men's clothing stores] decimal(18,2), 
    [Women's clothing stores] decimal(18,2),
    [Shoe stores] decimal(18,2),
    [Jewelry stores] decimal(18,2),
    [Sporting goods, hobby, musical instrument, and book stores] decimal(18,2),
    [General merchandise stores] decimal(18,2),
    [Department stores] decimal(18,2),
    [Other general merchandise stores] decimal(18,2), 
    [Warehouse clubs and superstores] decimal(18,2),
    [All other gen. merchandise stores] decimal(18,2),
    [Miscellaneous stores retailers] decimal(18,2),
    [Nonstore retailers] decimal(18,2),
    [Electronic shopping and mail order houses] decimal(18,2),
    [Fuel dealers] decimal(18,2),
    CONSTRAINT fk_Sales_by_categoryTable_DateID
        FOREIGN KEY (DateID)
        REFERENCES DateTable(DateID),
);
