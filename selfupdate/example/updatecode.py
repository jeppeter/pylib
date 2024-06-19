

def init_self_env():
	#signal.signal(signal.SIGINT,signal.SIG_IGN)
	signal.signal(signal.SIGTERM,signal.SIG_IGN)
	return True
