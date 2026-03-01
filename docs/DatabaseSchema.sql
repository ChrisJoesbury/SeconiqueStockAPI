-- Sanitised Schema for SeconiqueStockAPI
-- Contains only API-related tables, no definers, no Django admin/auth tables

DROP TABLE IF EXISTS `api_sitesettings`;
CREATE TABLE `api_sitesettings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `registration_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

DROP TABLE IF EXISTS `api_stocklevels`;
CREATE TABLE `api_stocklevels` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `partNum` varchar(11) NOT NULL,
  `partDesc` varchar(150) NOT NULL,
  `lastUpdatedDT` datetime(6) NOT NULL,
  `stockLev` int NOT NULL,
  `company` varchar(10) NOT NULL,
  `groupDesc` varchar(100) NOT NULL,
  `rangeName` varchar(100) NOT NULL,
  `subGroupDesc` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

DROP TABLE IF EXISTS `api_userprofile`;
CREATE TABLE `api_userprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `api_key` varchar(255) DEFAULT NULL,
  `user_id` int NOT NULL,
  `cust_ID` varchar(6) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `company_ID` varchar(10) DEFAULT NULL,
  `company_Name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- Sanitised Views (no definers)

DROP VIEW IF EXISTS `groupDescView`;
CREATE VIEW `groupDescView` AS
  SELECT DISTINCT `groupDesc` FROM `api_stocklevels`
  WHERE `groupDesc` IS NOT NULL AND `groupDesc` <> ''
  ORDER BY `groupDesc`;

DROP VIEW IF EXISTS `rangeNameView`;
CREATE VIEW `rangeNameView` AS
  SELECT DISTINCT `rangeName` FROM `api_stocklevels`
  WHERE `rangeName` IS NOT NULL AND `rangeName` <> ''
  ORDER BY `rangeName`;

DROP VIEW IF EXISTS `subGroupDescView`;
CREATE VIEW `subGroupDescView` AS
  SELECT DISTINCT `subGroupDesc` FROM `api_stocklevels`
  WHERE `subGroupDesc` IS NOT NULL AND `subGroupDesc` <> ''
  ORDER BY `subGroupDesc`;
