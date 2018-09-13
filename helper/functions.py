import hashlib

def md5sum(s):
	# accept one bytes argument
	if not isinstance(s, bytes):
		s = bytes(str(s), encoding='utf8')
	return hashlib.md5(s).hexdigest()

def strip(s):
	# accept one bytes argument
	return str(s).strip().strip('　')