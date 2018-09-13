def print_list_as_table(ll, headers=[]):
	column_width = 13
	head = ''
	hr = ''
	if headers:
		fmt = (('|{:^%d}' % column_width) * len(headers))+'|'
		head = fmt.format(*headers)
		hr = '|' + ('+'.join(['-'*column_width for i in range(len(headers))])) + '|'
	lines = [head, hr]
	for l in ll:
		if isinstance(l, list) or isinstance(l, tuple):
			fmt = (('|{:^%d}' % column_width) * len(l))+'|'
			lines.append(fmt.format(*l))
		else:
			fmt = '|{}|'
			lines.append(fmt.format(l))
	lines = [line.strip() for line in lines if line.strip()]
	print('\n'.join(lines))