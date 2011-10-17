-- MySQL dump 10.11
--
-- Host: localhost    Database: salathegroup_ts
-- ------------------------------------------------------
-- Server version	5.0.77

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `sentiment_controltweet`
--

DROP TABLE IF EXISTS `sentiment_controltweet`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `sentiment_controltweet` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `last_control_ordinal` bigint(20) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=67 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `sentiment_controltweet`
--

LOCK TABLES `sentiment_controltweet` WRITE;
/*!40000 ALTER TABLE `sentiment_controltweet` DISABLE KEYS */;
INSERT INTO `sentiment_controltweet` VALUES (3,26,761),(4,34,715),(5,5,413),(6,38,710),(7,1,14),(8,25,751),(9,12,808),(10,18,753),(11,28,1003),(12,14,758),(13,23,765),(14,15,41),(15,19,752),(16,21,750),(17,35,701),(18,40,702),(19,44,701),(20,43,37),(21,29,751),(22,17,953),(23,30,392),(24,33,851),(25,42,701),(26,37,275),(27,32,703),(28,39,701),(29,11,800),(30,3,753),(31,45,701),(32,51,705),(33,49,713),(34,50,738),(35,22,801),(36,54,701),(37,48,712),(38,53,702),(39,52,260),(40,56,702),(41,47,701),(42,60,703),(43,58,709),(44,16,752),(45,63,700),(46,13,761),(47,10,129),(48,62,352),(49,64,700),(50,6,752),(51,66,701),(52,65,375),(53,24,757),(54,20,53),(55,67,300),(56,41,701),(57,7,316),(58,68,704),(59,70,702),(60,4,754),(61,61,701),(62,59,702),(63,2,3),(64,36,76),(65,71,703),(66,27,752);
/*!40000 ALTER TABLE `sentiment_controltweet` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-01-19 15:45:31
