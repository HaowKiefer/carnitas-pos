/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: carnitas
-- ------------------------------------------------------
-- Server version	11.8.6-MariaDB-5ubuntu0.1 from Ubuntu

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `asistencias`
--

DROP TABLE IF EXISTS `asistencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `asistencias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `numero_empleado` int(11) NOT NULL,
  `tipo` enum('entrada','salida') NOT NULL,
  `fecha_hora` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `numero_empleado` (`numero_empleado`),
  CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`numero_empleado`) REFERENCES `empleados` (`numero_empleado`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asistencias`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `asistencias` WRITE;
/*!40000 ALTER TABLE `asistencias` DISABLE KEYS */;
INSERT INTO `asistencias` VALUES
(1,6,'entrada','2026-10-31 20:54:02'),
(2,6,'salida','2026-10-31 20:54:04'),
(3,6,'entrada','2026-10-31 20:54:04'),
(4,7,'entrada','2026-10-31 20:57:26'),
(5,7,'salida','2026-10-31 21:02:01'),
(6,6,'salida','2026-10-31 21:05:36'),
(7,7,'entrada','2026-10-31 21:05:51'),
(8,6,'entrada','2026-10-31 21:07:13'),
(9,8,'entrada','2026-11-03 11:58:22'),
(10,9,'entrada','2026-11-11 22:37:36'),
(11,11,'entrada','2026-11-11 23:13:20'),
(12,8,'salida','2026-11-11 23:13:21'),
(13,7,'salida','2026-11-11 23:13:22'),
(14,11,'salida','2026-11-11 23:13:23'),
(15,8,'entrada','2026-11-17 06:52:48'),
(16,7,'entrada','2026-11-17 06:55:48'),
(17,8,'salida','2026-11-17 06:56:03'),
(18,7,'salida','2026-11-17 06:56:03'),
(19,8,'entrada','2026-11-17 10:31:30');
/*!40000 ALTER TABLE `asistencias` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `bebida`
--

DROP TABLE IF EXISTS `bebida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bebida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bebida`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `bebida` WRITE;
/*!40000 ALTER TABLE `bebida` DISABLE KEYS */;
INSERT INTO `bebida` VALUES
(1,'COCOCHA',27.00),
(2,'Desechable',27.00),
(6,'Agua de Tamarindo',30.00),
(7,'Agua de Horchata',30.00);
/*!40000 ALTER TABLE `bebida` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `carne`
--

DROP TABLE IF EXISTS `carne`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `carne` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(60) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carne`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `carne` WRITE;
/*!40000 ALTER TABLE `carne` DISABLE KEYS */;
/*!40000 ALTER TABLE `carne` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `comida`
--

DROP TABLE IF EXISTS `comida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `comida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comida`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `comida` WRITE;
/*!40000 ALTER TABLE `comida` DISABLE KEYS */;
INSERT INTO `comida` VALUES
(5,'Tacos',30.00),
(6,'Gordita sencilla',30.00),
(7,'Gordita rellena',40.00),
(8,'Quesadillas',30.00),
(9,'Huaraches',50.00);
/*!40000 ALTER TABLE `comida` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleados` (
  `numero_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `usuario` varchar(50) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `rol` varchar(20) DEFAULT 'mesero',
  `direccion` varchar(150) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `en_turno` tinyint(1) DEFAULT 0,
  `intentos_fallidos` int(11) DEFAULT 0,
  `bloqueado_hasta` datetime DEFAULT NULL,
  PRIMARY KEY (`numero_empleado`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
INSERT INTO `empleados` VALUES
(2,'María','Fernández',NULL,NULL,'mesero','Calle Juárez 45, Col. Juárez','555-987-6543',0,0,0,NULL),
(3,'Juan','Rodríguez',NULL,NULL,'mesero','Av. Revolución 789, Col. Sur','555-456-7890',0,0,0,NULL),
(4,'Ana','García',NULL,NULL,'mesero','Calle Morelos 12, Col. Norte','555-321-6549',0,0,0,NULL),
(6,'Karla Samantha','Castillo Chavez',NULL,NULL,'mesero','12 Santiago Tianguistenco Amp. San Mateo, Estado de México','5519566089',0,0,0,NULL),
(7,'abel','zuniga','haow','kiefer','admin','socrates mz 4','5573218113',1,0,0,NULL),
(8,'Karla Samantha','Castillo Chavez','sam','ajonjoli','admin','12 Santiago Tianguistenco Amp. San Mateo, Estado de México','5519566089',1,1,0,NULL),
(9,'Login','usuario','log','log','admin','no','5510209399',0,0,0,NULL),
(11,'carlos','castillo','login','login','admin','estado de mexico','5541021342',0,0,0,NULL),
(12,'fds','fd','gfd','gfd','admin','ghfd fhdf','65464573',0,0,0,NULL);
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `extras`
--

DROP TABLE IF EXISTS `extras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `extras` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `extras`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `extras` WRITE;
/*!40000 ALTER TABLE `extras` DISABLE KEYS */;
INSERT INTO `extras` VALUES
(3,'Queso',10.00);
/*!40000 ALTER TABLE `extras` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `gastos`
--

DROP TABLE IF EXISTS `gastos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `gastos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `concepto` varchar(150) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `cantidad` decimal(10,2) DEFAULT 1.00,
  `unidad_medida` varchar(20) DEFAULT 'pza',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gastos`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `gastos` WRITE;
/*!40000 ALTER TABLE `gastos` DISABLE KEYS */;
INSERT INTO `gastos` VALUES
(1,'gas',100.00,'2026-10-31 19:56:50',1.00,'pza'),
(2,'carne',1300.00,'2026-10-31 21:39:09',15.00,'kg'),
(3,'COCOCHA',300.00,'2026-10-31 22:02:24',15.00,'pza'),
(4,'carne',400.00,'2026-11-03 09:11:32',7.00,'kg'),
(5,'masa',60.00,'2026-11-11 22:38:35',5.00,'kg'),
(6,'cebolla',19.00,'2026-11-11 23:14:03',4.00,'kg');
/*!40000 ALTER TABLE `gastos` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `historial_cambios_usuarios`
--

DROP TABLE IF EXISTS `historial_cambios_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_cambios_usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_admin` varchar(50) NOT NULL,
  `empleado_afectado` int(11) NOT NULL,
  `accion` varchar(50) NOT NULL,
  `detalles` varchar(255) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `empleado_afectado` (`empleado_afectado`),
  CONSTRAINT `historial_cambios_usuarios_ibfk_1` FOREIGN KEY (`empleado_afectado`) REFERENCES `empleados` (`numero_empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_cambios_usuarios`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `historial_cambios_usuarios` WRITE;
/*!40000 ALTER TABLE `historial_cambios_usuarios` DISABLE KEYS */;
INSERT INTO `historial_cambios_usuarios` VALUES
(1,'haow',4,'BAJA_LOGICA','Acceso desactivado para el usuario \'None\'.','2026-10-31 21:02:11'),
(2,'haow',3,'BAJA_LOGICA','Acceso desactivado para el usuario \'None\'.','2026-10-31 21:03:07'),
(3,'haow',2,'BAJA_LOGICA','Acceso desactivado para el usuario \'None\'.','2026-10-31 21:03:09'),
(4,'haow',6,'BAJA_LOGICA','Acceso desactivado para el usuario \'None\'.','2026-10-31 21:16:02'),
(5,'haow',8,'CREACION','Se creó el usuario \'sam\' con rol \'admin\'.','2026-10-31 21:16:52'),
(6,'sam',9,'CREACION','Se creó el usuario \'log\' con rol \'admin\'.','2026-11-11 22:37:24'),
(7,'sam',9,'BAJA_LOGICA','Acceso desactivado para el usuario \'log\'.','2026-11-11 22:37:43'),
(8,'haow',11,'CREACION','Se creó el usuario \'login\' con rol \'admin\'.','2026-11-11 23:13:15'),
(9,'haow',11,'BAJA_LOGICA','Acceso desactivado para el usuario \'login\'.','2026-11-11 23:13:26'),
(10,'haow',12,'CREACION','Se creó el usuario \'gfd\' con rol \'admin\'.','2026-11-11 23:17:24'),
(11,'haow',12,'BAJA_LOGICA','Acceso desactivado para el usuario \'gfd\'.','2026-11-11 23:17:26');
/*!40000 ALTER TABLE `historial_cambios_usuarios` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `inventario`
--

DROP TABLE IF EXISTS `inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto` varchar(100) NOT NULL,
  `cantidad` decimal(10,2) DEFAULT 0.00,
  `unidad_medida` varchar(20) DEFAULT 'pza',
  PRIMARY KEY (`id`),
  UNIQUE KEY `producto` (`producto`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `inventario` WRITE;
/*!40000 ALTER TABLE `inventario` DISABLE KEYS */;
INSERT INTO `inventario` VALUES
(1,'carne',7.60,'kg'),
(2,'COCOCHA',0.00,'pza'),
(3,'masa',5.00,'kg'),
(4,'cebolla',4.00,'kg');
/*!40000 ALTER TABLE `inventario` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `nomina`
--

DROP TABLE IF EXISTS `nomina`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `nomina` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `numero_empleado` int(11) NOT NULL,
  `horas_trabajadas` decimal(10,2) NOT NULL,
  `pago_por_hora` decimal(10,2) DEFAULT 37.80,
  `total_pagar` decimal(10,2) NOT NULL,
  `pagado` tinyint(1) DEFAULT 0,
  `fecha_registro` timestamp NULL DEFAULT current_timestamp(),
  `fecha_pago` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `numero_empleado` (`numero_empleado`),
  CONSTRAINT `nomina_ibfk_1` FOREIGN KEY (`numero_empleado`) REFERENCES `empleados` (`numero_empleado`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nomina`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `nomina` WRITE;
/*!40000 ALTER TABLE `nomina` DISABLE KEYS */;
INSERT INTO `nomina` VALUES
(2,8,0.05,37.80,1.89,0,'2026-11-17 12:56:03',NULL),
(3,7,0.01,37.80,0.38,0,'2026-11-17 12:56:03',NULL);
/*!40000 ALTER TABLE `nomina` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `ordenes`
--

DROP TABLE IF EXISTS `ordenes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mesa` int(11) NOT NULL,
  `producto` varchar(100) NOT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `cebolla` tinyint(1) DEFAULT 0,
  `cilantro` tinyint(1) DEFAULT 0,
  `nopales` tinyint(1) DEFAULT 0,
  `cantidad` int(11) DEFAULT 1,
  `fecha` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=350 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `ordenes` WRITE;
/*!40000 ALTER TABLE `ordenes` DISABLE KEYS */;
INSERT INTO `ordenes` VALUES
(345,1,'Tacos',30.00,0,0,0,1,'2026-11-12 05:15:33');
/*!40000 ALTER TABLE `ordenes` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_venta` varchar(100) NOT NULL,
  `id_inventario` int(11) NOT NULL,
  `cantidad_descuento` decimal(10,3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_inventario` (`id_inventario`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`id_inventario`) REFERENCES `inventario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES
(1,'Gordita rellena',1,0.200),
(2,'COCOCHA',2,1.000),
(3,'Gordita sencilla',1,0.150),
(4,'Huaraches',1,0.200),
(5,'Huaraches',3,0.100);
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_venta` int(11) DEFAULT NULL,
  `mesa` varchar(20) NOT NULL,
  `producto` varchar(100) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `cebolla` tinyint(1) DEFAULT 0,
  `cilantro` tinyint(1) DEFAULT 0,
  `nopales` tinyint(1) DEFAULT 0,
  `subtotal` decimal(10,2) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES
(28,1,'4','Tacos',30.00,4,0,0,0,120.00,'2026-10-31 19:52:41'),
(29,1,'4','Gordita rellena',40.00,4,0,0,0,160.00,'2026-10-31 19:52:41'),
(30,2,'5','Tacos',30.00,2,1,1,1,60.00,'2026-10-31 21:27:10'),
(31,2,'5','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-10-31 21:27:10'),
(32,3,'1','Tacos',30.00,1,0,0,0,30.00,'2026-10-31 21:51:17'),
(33,3,'1','Huaraches',50.00,1,0,0,0,50.00,'2026-10-31 21:51:17'),
(34,3,'1','Quesadillas',30.00,1,0,0,0,30.00,'2026-10-31 21:51:17'),
(35,3,'1','Gordita rellena',40.00,1,0,0,0,40.00,'2026-10-31 21:51:17'),
(36,3,'1','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-10-31 21:51:17'),
(37,3,'1','uwuuw',100.00,1,0,0,0,100.00,'2026-10-31 21:51:17'),
(38,4,'1','COCOCHA',27.00,1,0,0,0,27.00,'2026-10-31 22:02:37'),
(39,5,'1','COCOCHA',27.00,4,0,0,0,108.00,'2026-10-31 22:04:26'),
(40,6,'1','Tacos',30.00,1,0,0,0,30.00,'2026-11-03 12:02:53'),
(41,6,'1','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-11-03 12:02:53'),
(42,6,'1','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-11-03 12:02:53'),
(43,7,'2','tortas',30.00,1,0,0,0,30.00,'2026-11-03 12:03:39'),
(44,7,'2','tortas',30.00,1,0,0,0,30.00,'2026-11-03 12:03:39'),
(45,7,'2','tortas',30.00,1,0,0,0,30.00,'2026-11-03 12:03:39'),
(46,7,'2','Quesadillas',30.00,1,1,1,1,30.00,'2026-11-03 12:03:39'),
(47,7,'2','Tacos',30.00,1,0,0,0,30.00,'2026-11-03 12:03:39'),
(48,7,'2','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-11-03 12:03:39'),
(49,7,'2','Gordita rellena',40.00,1,0,0,0,40.00,'2026-11-03 12:03:39'),
(50,8,'6','Tacos',30.00,1,0,0,0,30.00,'2026-11-03 12:16:18'),
(51,8,'6','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-11-03 12:16:18'),
(52,8,'6','Tacos',30.00,1,0,0,0,30.00,'2026-11-03 12:16:18'),
(53,8,'6','Tacos',30.00,1,0,0,0,30.00,'2026-11-03 12:16:18'),
(54,8,'6','Agua de Tamarindo',30.00,1,0,0,0,30.00,'2026-11-03 12:16:18'),
(55,8,'6','Gordita sencilla',30.00,1,0,0,1,30.00,'2026-11-03 12:16:18'),
(56,9,'2','Tacos',30.00,1,0,0,0,30.00,'2026-11-05 11:22:09'),
(57,9,'2','Gordita sencilla',30.00,1,0,0,0,30.00,'2026-11-05 11:22:09'),
(58,9,'2','COCOCHA',27.00,1,0,0,0,27.00,'2026-11-05 11:22:09'),
(59,9,'2','COCOCHA',27.00,7,0,0,0,189.00,'2026-11-05 11:22:09'),
(60,10,'1','Desechable',27.00,3,0,0,0,81.00,'2026-11-11 22:41:06'),
(61,10,'1','Tacos',30.00,3,1,1,0,90.00,'2026-11-11 22:41:06'),
(62,10,'1','Tacos',30.00,1,0,0,0,30.00,'2026-11-11 22:41:06'),
(63,10,'1','Queso',10.00,1,0,0,0,10.00,'2026-11-11 22:41:06'),
(64,11,'2','COCOCHA',27.00,1,0,0,0,27.00,'2026-11-11 22:41:22'),
(65,12,'2','COCOCHA',27.00,4,0,0,0,108.00,'2026-11-11 23:16:08'),
(66,12,'2','Agua de Tamarindo',30.00,1,0,0,0,30.00,'2026-11-11 23:16:08'),
(67,12,'2','Tacos',30.00,2,1,1,1,60.00,'2026-11-11 23:16:08'),
(68,12,'2','Queso',10.00,1,0,0,0,10.00,'2026-11-11 23:16:08');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-11-17 11:58:35
