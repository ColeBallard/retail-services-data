drop database if exists [capstone-group6-database];
GO

create database [capstone-group6-database];
GO

use [capstone-group6-database];
GO

CREATE TABLE DateTable (
    DateID int PRIMARY KEY IDENTITY(1,1),
    DateYear INT NOT NULL,
    DateMonth INT, 
    DateDay int
);

CREATE TABLE MacroTable(
    MacroID INT PRIMARY KEY IDENTITY(1,1),
    DateID INT NOT NULL,
    CPI DECIMAL,
    RPI DECIMAL,
    USTRADE DECIMAL,
    USWTRADE DECIMAL,
    CONSTRAINT fk_MacroTable_DateID
        FOREIGN KEY (DateID)
        REFERENCES DateTable(DateID)
);

CREATE TABLE NAICSTable (
    NAICSID INT PRIMARY KEY IDENTITY(1,1),
    NAICSname VARCHAR(50),
    NAICSCode INT
);

CREATE TABLE SalesTable (
    SalesID INT PRIMARY KEY IDENTITY(1,1),
    DateID INT,
    NAICSID INT,
    AdjustedSales DECIMAL,
    Sales DECIMAL,
    CONSTRAINT fk_SalesTable_DateID
        FOREIGN KEY (DateID)
        REFERENCES DateTable(DateID),
    CONSTRAINT fk_SalesTable_NAICSID
        FOREIGN KEY (NAICSID)
        REFERENCES NAICSTable(NAICSID)
);

CREATE TABLE NAPCSTable (
    NAPCSID INT PRIMARY KEY IDENTITY(1,1),
    NAPCSCode INT,
    NAPCSName VARCHAR(50)
);

CREATE TABLE NAISC_NAPCS (
    NAICSID INT,
    NAPCSID INT,
    NumberofEstablishments INT,
    SalesValueofshipmentsorRevenue INT,
    PRIMARY KEY (NAICSID, NAPCSID),
    CONSTRAINT fk_NAISC_NAPCS_NAICSID
        FOREIGN KEY (NAICSID)
        REFERENCES NAICSTable(NAICSID),
    CONSTRAINT fk_NAISC_NAPCS_NAPCSID
        FOREIGN KEY (NAPCSID)
        REFERENCES NAPCSTable(NAPCSID)
)