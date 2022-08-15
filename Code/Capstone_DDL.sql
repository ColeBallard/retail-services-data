drop table if exists SalesTable;
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