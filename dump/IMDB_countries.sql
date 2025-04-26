-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: bernardo.ddns.net    Database: IMDB
-- ------------------------------------------------------
-- Server version	8.0.41-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` VALUES ('AE','United Arab Emirates'),('AL','Albania'),('AR','Argentina'),('AT','Austria'),('AU','Australia'),('BA','Bosnia and Herzegovina'),('BD','Bangladesh'),('BE','Belgium'),('BG','Bulgaria'),('BJ','Benin'),('BR','Brazil'),('BT','Bhutan'),('CA','Canada'),('CH','Switzerland'),('CL','Chile'),('CN','China'),('CO','Colombia'),('CY','Cyprus'),('CZ','Czechia'),('DE','Germany'),('DK','Denmark'),('DO','Dominican Republic'),('DZ','Algeria'),('EE','Estonia'),('EG','Egypt'),('ES','Spain'),('FI','Finland'),('FR','France'),('GB','United Kingdom'),('GE','Georgia'),('GM','Gambia'),('GR','Greece'),('HK','Hong Kong'),('HR','Croatia'),('HT','Haiti'),('HU','Hungary'),('ID','Indonesia'),('IE','Ireland'),('IL','Israel'),('IN','India'),('IR','Iran, Islamic Republic of'),('IS','Iceland'),('IT','Italy'),('JO','Jordan'),('JP','Japan'),('KH','Cambodia'),('KR','Korea, Republic of'),('LB','Lebanon'),('LK','Sri Lanka'),('LT','Lithuania'),('LU','Luxembourg'),('LV','Latvia'),('MA','Morocco'),('ME','Montenegro'),('MK','North Macedonia'),('MT','Malta'),('MU','Mauritius'),('MX','Mexico'),('NG','Nigeria'),('NL','Netherlands'),('NO','Norway'),('NZ','New Zealand'),('PA','Panama'),('PE','Peru'),('PH','Philippines'),('PK','Pakistan'),('PL','Poland'),('PR','Puerto Rico'),('PS','Palestine, State of'),('PT','Portugal'),('QA','Qatar'),('RO','Romania'),('RS','Serbia'),('RU','Russian Federation'),('SA','Saudi Arabia'),('SE','Sweden'),('SG','Singapore'),('SI','Slovenia'),('SK','Slovakia'),('SN','Senegal'),('SUHH','SUHH'),('TH','Thailand'),('TN','Tunisia'),('TR','Türkiye'),('TW','Taiwan, Province of China'),('UA','Ukraine'),('US','United States'),('VN','Viet Nam'),('XWG','XWG'),('ZA','South Africa'),('ZM','Zambia');
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-26 16:20:57
