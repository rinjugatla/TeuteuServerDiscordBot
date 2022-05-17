-- ---
-- Globals
-- ---

-- SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
-- SET FOREIGN_KEY_CHECKS=0;

-- ---
-- Table 'tts_files'
-- 
-- ---

DROP TABLE IF EXISTS `tts_files`;
		
CREATE TABLE `tts_files` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `text` VARCHAR(4000) NOT NULL,
  `hash` VARCHAR(100) NOT NULL,
  `extension` VARCHAR(4) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT current_timestamp(),
  `updated_at` DATETIME NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'tts_words'
-- 
-- ---

DROP TABLE IF EXISTS `tts_words`;
		
CREATE TABLE `tts_words` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `pattern` VARCHAR(200) NOT NULL,
  `replace` VARCHAR(200) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT current_timestamp(),
  `updated_at` DATETIME NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'apex_users'
-- 
-- ---

DROP TABLE IF EXISTS `apex_users`;
		
CREATE TABLE `apex_users` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `name` INTEGER NOT NULL,
  `uid` INTEGER NOT NULL,
  `platform` INTEGER NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT current_timestamp(),
  `updated_at` DATETIME NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);

-- ---
-- Table 'apex_user_rank'
-- 
-- ---

DROP TABLE IF EXISTS `apex_user_rank`;
		
CREATE TABLE `apex_user_rank` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `apex_user_id` INTEGER NOT NULL,
  `season` INTEGER NOT NULL,
  `split` INTEGER NOT NULL,
  `battle_score` INTEGER NOT NULL,
  `battle_name` VARCHAR(20) NOT NULL,
  `battle_division` INTEGER NOT NULL,
  `arena_score` INTEGER NOT NULL,
  `arena_name` VARCHAR(20) NOT NULL,
  `arena_division` INTEGER NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT current_timestamp(),
  `updated_at` DATETIME NOT NULL DEFAULT DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);

-- ---
-- Foreign Keys 
-- ---

ALTER TABLE `apex_user_rank` ADD FOREIGN KEY (apex_user_id) REFERENCES `apex_users` (`id`);

-- ---
-- Table Properties
-- ---

-- ALTER TABLE `tts_files` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `tts_words` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `apex_users` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- ALTER TABLE `apex_user_rank` ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ---
-- Test Data
-- ---

-- INSERT INTO `tts_files` (`id`,`text`,`hash`,`extension`,`created_at`,`updated_at`) VALUES
-- ('','','','','','');
-- INSERT INTO `tts_words` (`id`,`pattern`,`replace`,`created_at`,`updated_at`) VALUES
-- ('','','','','');
-- INSERT INTO `apex_users` (`id`,`name`,`uid`,`platform`,`created_at`,`updated_at`) VALUES
-- ('','','','','','');
-- INSERT INTO `apex_user_rank` (`id`,`apex_user_id`,`season`,`split`,`battle_score`,`battle_name`,`battle_division`,`arena_score`,`arena_name`,`arena_division`,`created_at`,`updated_at`) VALUES
-- ('','','','','','','','','','','','');