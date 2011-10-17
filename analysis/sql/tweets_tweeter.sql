ALTER TABLE tweets_tweet ADD COLUMN tweeter_id integer;

ALTER TABLE `tweets_tweet` ADD CONSTRAINT `tweeter_id_refs_id_e4dd7605` FOREIGN KEY (`tweeter_id`) REFERENCES `tweeter_tweeter` (`id`);COMMIT;
