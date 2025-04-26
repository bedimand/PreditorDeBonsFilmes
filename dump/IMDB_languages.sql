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
-- Table structure for table `languages`
--

DROP TABLE IF EXISTS `languages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `languages` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `languages`
--

LOCK TABLES `languages` WRITE;
/*!40000 ALTER TABLE `languages` DISABLE KEYS */;
INSERT INTO `languages` VALUES ('af','af'),('ak','ak'),('am','am'),('ar','ar'),('be','be'),('bg','bg'),('bn','bn'),('ca','ca'),('Cantonese','Cantonese'),('ce','ce'),('cmn','cmn'),('cs','cs'),('cy','cy'),('da','da'),('de','de'),('dz','dz'),('el','el'),('en','en'),('eo','eo'),('es','es'),('et','et'),('fa','fa'),('fi','fi'),('fr','fr'),('ga','ga'),('gd','gd'),('gl','gl'),('gu','gu'),('he','he'),('hi','hi'),('hr','hr'),('ht','ht'),('hu','hu'),('hy','hy'),('id','id'),('is','is'),('it','it'),('iu','iu'),('ja','ja'),('ka','ka'),('ki','ki'),('kl','kl'),('kn','kn'),('ko','ko'),('ku','ku'),('la','la'),('lb','lb'),('lt','lt'),('lv','lv'),('Mandarin','Mandarin'),('mi','mi'),('mk','mk'),('ml','ml'),('mn','mn'),('mr','mr'),('ms','ms'),('mt','mt'),('my','my'),('nan','nan'),('ne','ne'),('nl','nl'),('no','no'),('oj','oj'),('or','or'),('pa','pa'),('pl','pl'),('pt','pt'),('qu','qu'),('ro','ro'),('ru','ru'),('rw','rw'),('sa','sa'),('sgn','sgn'),('si','si'),('sk','sk'),('sl','sl'),('sm','sm'),('so','so'),('sq','sq'),('sr','sr'),('sv','sv'),('sw','sw'),('ta','ta'),('te','te'),('th','th'),('tl','tl'),('tr','tr'),('uk','uk'),('ur','ur'),('vi','vi'),('wo','wo'),('xh','xh'),('yi','yi'),('yue','yue'),('zh','zh'),('zu','zu');
/*!40000 ALTER TABLE `languages` ENABLE KEYS */;
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
