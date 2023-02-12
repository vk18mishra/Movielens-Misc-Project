CREATE DATABASE  IF NOT EXISTS `movielens_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `movielens_db`;
-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: movielens_db
-- ------------------------------------------------------
-- Server version	8.0.31

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
-- Table structure for table `avg_rating_count`
--

DROP TABLE IF EXISTS `avg_rating_count`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `avg_rating_count` (
  `movieId` int NOT NULL,
  `rating` float DEFAULT NULL,
  `rating_count` int DEFAULT NULL,
  PRIMARY KEY (`movieId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
/*!50100 PARTITION BY RANGE (`movieId`)
(PARTITION p0 VALUES LESS THAN (6354) ENGINE = InnoDB,
 PARTITION p1 VALUES LESS THAN (60382) ENGINE = InnoDB,
 PARTITION p2 VALUES LESS THAN (97845) ENGINE = InnoDB,
 PARTITION p3 VALUES LESS THAN (122709) ENGINE = InnoDB,
 PARTITION p4 VALUES LESS THAN (138024) ENGINE = InnoDB,
 PARTITION p5 VALUES LESS THAN (152682) ENGINE = InnoDB,
 PARTITION p6 VALUES LESS THAN (166631) ENGINE = InnoDB,
 PARTITION p7 VALUES LESS THAN (179933) ENGINE = InnoDB,
 PARTITION p8 VALUES LESS THAN (193599) ENGINE = InnoDB,
 PARTITION p9 VALUES LESS THAN (209172) ENGINE = InnoDB) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `links`
--

DROP TABLE IF EXISTS `links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `links` (
  `movieId` int NOT NULL,
  `imdbId` varchar(45) DEFAULT NULL,
  `tmdbId` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`movieId`),
  CONSTRAINT `links_to_movies` FOREIGN KEY (`movieId`) REFERENCES `movies_new` (`movieId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movies_new`
--

DROP TABLE IF EXISTS `movies_new`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies_new` (
  `movieId` int NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `Adventure` int DEFAULT NULL,
  `Animation` int DEFAULT NULL,
  `Children` int DEFAULT NULL,
  `Comedy` int DEFAULT NULL,
  `Fantasy` int DEFAULT NULL,
  `Romance` int DEFAULT NULL,
  `Drama` int DEFAULT NULL,
  `Action` int DEFAULT NULL,
  `Crime` int DEFAULT NULL,
  `Thriller` int DEFAULT NULL,
  `Horror` int DEFAULT NULL,
  `Mystery` int DEFAULT NULL,
  `Sci_Fi` int DEFAULT NULL,
  `IMAX` int DEFAULT NULL,
  `Documentary` int DEFAULT NULL,
  `War` int DEFAULT NULL,
  `Musical` int DEFAULT NULL,
  `Western` int DEFAULT NULL,
  `Film_Noir` int DEFAULT NULL,
  `no_genres_listed` int DEFAULT NULL,
  PRIMARY KEY (`movieId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ratings` (
  `userId` int NOT NULL,
  `movieId` int NOT NULL,
  `rating` float DEFAULT NULL,
  PRIMARY KEY (`movieId`,`userId`),
  KEY `userId_index` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
/*!50100 PARTITION BY RANGE (`movieId`)
(PARTITION p0 VALUES LESS THAN (356) ENGINE = InnoDB,
 PARTITION p1 VALUES LESS THAN (898) ENGINE = InnoDB,
 PARTITION p2 VALUES LESS THAN (1295) ENGINE = InnoDB,
 PARTITION p3 VALUES LESS THAN (2081) ENGINE = InnoDB,
 PARTITION p4 VALUES LESS THAN (2947) ENGINE = InnoDB,
 PARTITION p5 VALUES LESS THAN (4148) ENGINE = InnoDB,
 PARTITION p6 VALUES LESS THAN (6478) ENGINE = InnoDB,
 PARTITION p7 VALUES LESS THAN (44191) ENGINE = InnoDB,
 PARTITION p8 VALUES LESS THAN (81847) ENGINE = InnoDB,
 PARTITION p9 VALUES LESS THAN (209172) ENGINE = InnoDB) */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_clustering`
--

DROP TABLE IF EXISTS `user_clustering`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_clustering` (
  `userId` int NOT NULL,
  `rating` float DEFAULT NULL,
  `Adventure` int DEFAULT NULL,
  `Animation` int DEFAULT NULL,
  `Children` int DEFAULT NULL,
  `Comedy` int DEFAULT NULL,
  `Fantasy` int DEFAULT NULL,
  `Romance` int DEFAULT NULL,
  `Drama` int DEFAULT NULL,
  `Action` int DEFAULT NULL,
  `Crime` int DEFAULT NULL,
  `Thriller` int DEFAULT NULL,
  `Horror` int DEFAULT NULL,
  `Mystery` int DEFAULT NULL,
  `Sci_Fi` int DEFAULT NULL,
  `IMAX` int DEFAULT NULL,
  `Documentary` int DEFAULT NULL,
  `War` int DEFAULT NULL,
  `Musical` int DEFAULT NULL,
  `Western` int DEFAULT NULL,
  `Film_Noir` int DEFAULT NULL,
  `no_genres_listed` int DEFAULT NULL,
  PRIMARY KEY (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-02-08 16:03:02
