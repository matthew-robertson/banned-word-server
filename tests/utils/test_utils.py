from bannedWordServer.models import Server, ServerPlan, Plan, Ban, BanRecord

def create_server(session, banned_words=None, server_id="1234", bannings_allowed=3, plan_name="Test Plan", plan_id=1):
	if not banned_words:
		new_ban = Ban(server_id=int(server_id))
		ban_record = BanRecord(server_banned_word=new_ban)
		session.add(new_ban)
		session.add(ban_record)
		banned_words=[new_ban]

	plan = session.query(Plan).filter_by(plan_id=plan_id).first()
	if not plan:
		plan = Plan(plan_id=plan_id, name=plan_name, bannings_allowed=bannings_allowed)
		session.add(plan)

	server = Server(server_id=int(server_id), banned_words=banned_words)
	session.add(server)
	server_plan=ServerPlan(plan_id=plan_id, server_id=int(server_id))
	session.add(server_plan)

	return server, plan