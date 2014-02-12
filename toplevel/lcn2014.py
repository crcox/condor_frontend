def parse_expfile(filename):
# Establish valid parameters.
	ValidParameters = ['muset','lamset','cvmethod','narb','shuffle','shufflemethod','GroupSize','GroupShift']
	args = {key: None for key in ValidParameters}

# Parse text to dictionary, checking that all parameters
# are valid for this experiment.
	with open(filename,'r') as f:
		for line in f:
			temp = line.strip().split(':')
			carg = temp.pop(0)
			try:
				args[carg]
				args[carg] = [x.strip() for x in temp[0].lstrip().split(' ')]
			except KeyError:
				print "\nERROR: ''%s'' is not a valid argument for this experiment!\n" % carg
				raise

# Check that no values are missing. Report if any are.
	MissingArgs = [x == None for x in args.values()]
	MissingArgKeys = [x for x,y in args.items() if y == None]
	if any(MissingArgs):
		print "\nERROR: values for %s are missing.\n" % MissingArgKeys
		return

# Setup file-structure.
	try:
		os.mkdir('lib')
	except OSError:
		"\nERROR: 'lib/' already exists in this directory. Did you remember to create a new directory for this experiment?\n"
		return
	
	with open('lib/NSet.txt','w') as f:
		f.write(' '.join(args['lamset'])+'\n')
	
	with open('lib/LambdaSet.txt','w') as f:
		f.write(' '.join(args['lamset'])+'\n')
	
	with open('lib/LambdaSet.txt','w') as f:
		f.write(' '.join(args['lamset'])+'\n')
	
	with open('lib/LambdaSet.txt','w') as f:
		f.write(' '.join(args['lamset'])+'\n')
	
	with open('lib/MuSet.txt','w') as f:
		f.write(' '.join(args['muset'])+'\n')
	
	with open('lib/GroupSize.txt','w') as f:
		f.write(' '.join(args['GroupSize'])+'\n')
	
	gsz = int(args['GroupSize'][0])
	if args['GroupShift'][0] == "+":
		Shift = gsz-(gsz/2)
	elif args['GroupShift'][0] == "-":
		Shift = gsz/2
	else:
		Shift = args['GroupShift']

	with open('lib/GroupShift.txt','w') as f:
		f.write(str(Shift)+'\n')
