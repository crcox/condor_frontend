def nonblank_lines(f):
	for l in f:
		line = l.rstrip()
		if line:
			yield line

def parse(filename):
	import os
	EXPNAME="lcn2014"
	[expinfo,ext] = os.path.splitext(os.path.basename(filename))
	print expinfo
	try:
		[expname,expnum] = expinfo.split('_')
	except ValueError:
		print "\nERROR: The filename does not follow convention 'expcode_expnum.txt'.\n"
		return 1

	if not EXPNAME == expname:
		print "\nERROR: Experiment code does not match the code that this module expects! Check your file name.\n"
		return 1
	

	CommentChars = ["#","/"]
# Establish valid parameters.
	ValidParameters = ['GroupSparseVals','SparseVals','CrossValidationMethod','AddArbitraryByLayer','ShuffleByLayer','ShuffleMethod','GroupSize','GroupShift']
	args = {key: None for key in ValidParameters}

# Parse text to dictionary, checking that all parameters
# are valid for this experiment.
	with open(filename,'r') as f:
		for line in nonblank_lines(f):
			if line[0] in CommentChars:
				continue
			temp = line.strip().split(':')
			carg = temp.pop(0)
			try:
				args[carg]
				args[carg] = [x.strip() for x in temp[0].lstrip().split(' ')]
			except KeyError:
				print "\nERROR: ''%s'' is not a valid argument for this experiment!\n" % carg
				return 2

# Check that no values are missing. Report if any are.
	MissingArgs = [x == None for x in args.values()]
	MissingArgKeys = [x for x,y in args.items() if y == None]
	if any(MissingArgs):
		print "\nERROR: values for %s are missing.\n" % MissingArgKeys
		return 3

# Setup file-structure.
	try:
		os.mkdir(expinfo)
	except OSError:
		print "\nERROR: 'An project already exists for this expcode and number.\n"
		return 4

	os.mkdir('%s/shared/' % expinfo)

	# This experiment will have separate jobs for each level of mu.
	for ii,mm in enumerate(args['GroupSparseVals']):
		os.mkdir('%s/%d/' % (expinfo,ii+1))
		with open('%s/%d/WhichMu.txt' % (expinfo,ii+1),'w') as f:
			f.write(str(ii+1)+'\n')
	
	os.chdir('%s/shared/' % expinfo)
	
	gsz = int(args['GroupSize'][0])
	if args['GroupShift'][0] == "+":
		args['GroupShift'] = str(gsz-(gsz/2))
	elif args['GroupShift'][0] == "-":
		args['GroupShift'] = str(gsz/2)
	
	for key,val in args.items():
		with open('%s.txt' % key,'w') as f:
			f.write(' '.join(val)+'\n')
