# GLOBAL VARIABLES
CommentChars = ["#","/"]

ValidParameters = ['SparseVals','TargetCategory','MeanCenter','NormVariance']
args = {key: None for key in ValidParameters}

def nonblank_lines(f):
	for l in f:
		line = l.rstrip()
		if line:
			yield line

def parse(filename):
	import os, subprocess
	EXPNAME="jlp+lasso"
	[expinfo,ext] = os.path.splitext(os.path.basename(filename))
	try:
		[expname,expnum] = expinfo.split('_')
	except ValueError:
		print "\nERROR: The filename does not follow convention 'expcode+expnum.txt'.\n"
		return 1

	if not EXPNAME == expname:
		print "\nERROR: Experiment code does not match the code that this module expects! Check your file name.\n"
		return 1
	
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
		print "\nERROR: 'A project already exists for this expcode and number.\n"
		return 4

	os.mkdir('%s/shared/' % expinfo)

	# This experiment will have separate jobs for each Hold out set and level of mu.
	# Each job will do 9-fold CV over a set of lambda.
	ncv = 10;
	nsub = 10;
	for i in range(ncv):
		for j in range(nsub):
			job = (i*nsub) + j
			os.mkdir('%s/%03d/' % (expinfo,job+1))
			with open('%s/%03d/WhichCV.txt' % (expinfo,job+1),'w') as f:
				f.write(str(i+1)+'\n')
			with open('%s/%03d/WhichSubject.txt' % (expinfo,job+1),'w') as f:
				f.write(str(j+1)+'\n')
			with open('%s/%03d/URLS' % (expinfo,job+1),'w') as f:
				f.write('/crcox/jlp%02d.mat\n' % (j+1))
	
	for key,val in args.items():
		with open('%s/shared/%s.txt' % (expinfo,key),'w') as f:
			f.write(' '.join(val)+'\n')

	subprocess.call(['rsync','-avz',expinfo+'/',"crcox@chtc:jlp+lasso/Exp%02d" % int(expnum)])
	subprocess.call(['ssh','crcox@chtc','cp ~/src/jlp+lasso/bin/jlp+cvlasso_condor ~/jlp+lasso/Exp%02d/shared/jlp+cvlasso_condor' % int(expnum)])
	
	return 0

