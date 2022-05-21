-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- ホスト: 127.0.0.1
-- 生成日時: 2022-05-21 13:21:16
-- サーバのバージョン： 10.7.3-MariaDB
-- PHP のバージョン: 8.1.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- データベース: `teuteu_discord_server`
--
CREATE DATABASE IF NOT EXISTS `teuteu_discord_server` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `teuteu_discord_server`;

-- --------------------------------------------------------

--
-- テーブルの構造 `apex_users`
--

CREATE TABLE `apex_users` (
  `id` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `uid` bigint(20) NOT NULL,
  `platform` varchar(4) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- テーブルの構造 `apex_user_ranks`
--

CREATE TABLE `apex_user_ranks` (
  `id` int(11) NOT NULL,
  `apex_user_id` int(11) NOT NULL,
  `season` int(11) NOT NULL,
  `split` int(11) NOT NULL,
  `battle_score` int(11) NOT NULL,
  `battle_name` varchar(20) NOT NULL,
  `battle_division` int(11) NOT NULL,
  `arena_score` int(11) NOT NULL,
  `arena_name` varchar(20) NOT NULL,
  `arena_division` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- テーブルの構造 `tts_files`
--

CREATE TABLE `tts_files` (
  `id` int(11) NOT NULL,
  `text` varchar(4000) NOT NULL,
  `hash` varchar(200) NOT NULL,
  `extension` varchar(4) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- テーブルの構造 `tts_words`
--

CREATE TABLE `tts_words` (
  `id` int(11) NOT NULL,
  `pattern` varchar(100) NOT NULL,
  `new` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- ダンプしたテーブルのインデックス
--

--
-- テーブルのインデックス `apex_users`
--
ALTER TABLE `apex_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_01` (`uid`) USING BTREE;

--
-- テーブルのインデックス `apex_user_ranks`
--
ALTER TABLE `apex_user_ranks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_01` (`apex_user_id`);

--
-- テーブルのインデックス `tts_files`
--
ALTER TABLE `tts_files`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_01` (`hash`);

--
-- テーブルのインデックス `tts_words`
--
ALTER TABLE `tts_words`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_01` (`pattern`);

--
-- ダンプしたテーブルの AUTO_INCREMENT
--

--
-- テーブルの AUTO_INCREMENT `apex_users`
--
ALTER TABLE `apex_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- テーブルの AUTO_INCREMENT `apex_user_ranks`
--
ALTER TABLE `apex_user_ranks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- テーブルの AUTO_INCREMENT `tts_files`
--
ALTER TABLE `tts_files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- テーブルの AUTO_INCREMENT `tts_words`
--
ALTER TABLE `tts_words`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `apex_user_ranks`
--
ALTER TABLE `apex_user_ranks`
  ADD CONSTRAINT `ref_apex_users_id` FOREIGN KEY (`apex_user_id`) REFERENCES `apex_users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
