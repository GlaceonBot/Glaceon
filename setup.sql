CREATE TABLE IF NOT EXISTS settings (serverid BIGINT, setto BIGINT, setting TEXT);
CREATE TABLE IF NOT EXISTS whitelisted_invites (hostguild BIGINT, inviteguild BIGINT);
CREATE TABLE IF NOT EXISTS current_bans (serverid BIGINT,  userid BIGINT, banfinish BIGINT);
CREATE TABLE IF NOT EXISTS current_mutes (serverid BIGINT,  userid BIGINT, mutefinish BIGINT);
CREATE TABLE IF NOT EXISTS current_mutes (serverid BIGINT,  userid BIGINT, mutefinish BIGINT);
CREATE TABLE IF NOT EXISTS current_bans (serverid BIGINT,  userid BIGINT, banfinish BIGINT);
CREATE TABLE IF NOT EXISTS tags (serverid BIGINT, tagname TEXT, tagcontent TEXT);
CREATE TABLE IF NOT EXISTS prefixes (serverid BIGINT, prefix TEXT);
CREATE TABLE IF NOT EXISTS disabled_commands (serverid BIGINT, commandname TEXT, state BIT);
