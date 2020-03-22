CREATE OR REPLACE FUNCTION calc_total_virginity (virginid text, guildid text, latestVCTime double precision) 
  RETURNS int AS $$
DECLARE
  POINTS_PER_MINUTE double precision = 5.0; 
  BOT_SCORE_MULTIPLIER double precision = 0.5;
  vc_time double precision = 0.0;
  bot boolean = FALSE;
  virginity_score double precision = 0.0;
BEGIN
	SELECT total_vc_time, is_bot 
	INTO vc_time, bot
	FROM public.Virgin
	WHERE Virgin.id = virginid AND Virgin.guild_id = guildid;
	
	virginity_score = ((vc_time+latestVCTime)/60) * POINTS_PER_MINUTE ;
	
	if bot = TRUE THEN
		 virginity_score = virginity_score * BOT_SCORE_MULTIPLIER;
	END IF;
	
	virginity_score = floor(virginity_score);
	
	return virginity_score;
	
END;
$$ LANGUAGE plpgsql;
