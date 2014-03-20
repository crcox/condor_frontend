import os, subprocess
EXPNAME='lcn+soslasso'
params = {'pathToBinary':'~/src/lcn+soslasso/bin/lcn+soslasso', 'cmdtorun':'lcn+soslasso', 'expinfo':None,'outPattern':'lcn+soslasso_wd001_nh7_*.mat','data':'9c2.mat','host':'crcox@chtc'}

CommentChars = ["#","/"]
# Establish valid parameters.
ValidParameters = ['GroupSparseVals','SparseVals','WhichCVMethod','NumberOfArbVox','WhichShuffle','WhichShuffleMethod','GroupSize','GroupShift']
args = {key: None for key in ValidParameters}

def nonblank_lines(f):
	for l in f:
		line = l.rstrip()
		if line:
			yield line

def parse(filename):
	[params['expinfo'],ext] = os.path.splitext(os.path.basename(filename))
	try:
		[expname,expnum] = params['expinfo'].split('_')
	except ValueError:
		print "\nERROR: The filename does not follow convention 'expcode_expnum.txt'.\n"
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
		os.mkdir(params['expinfo'])
	except OSError:
		print "\nERROR: 'An project already exists for this expcode and number.\n"
		return 4

	os.mkdir('%(expinfo)s/shared/' % params)

	# This experiment will have separate jobs for each level of mu, and group size
	for ii,mm in enumerate(args['GroupSparseVals']):
		filename = os.path.join(params['expinfo'],str(ii+1))
		os.mkdir(filename)
		filename = os.path.join(params['expinfo'],str(ii+1),'WhichMu.txt')
		with open(filename,'w') as f:
			f.write(str(ii+1)+'\n')
	
	gsz = int(args['GroupSize'][0])
	if args['GroupShift'][0] == "+":
		args['GroupShift'] = str(gsz-(gsz/2))
	elif args['GroupShift'][0] == "-":
		args['GroupShift'] = str(gsz/2)
	
	for key,val in args.items():
		filename=os.path.join(params['expinfo'],'shared',key+'.txt')
		with open(filename,'w') as f:
			f.write(' '.join(val)+'\n')

	filename=os.path.join(params['expinfo'],'shared','URLS.txt')
	with open(filename,'w') as f:
		f.write('/squid/crcox/%(data)s\n' % params)

	subprocess.call(['rsync','-avz',params['expinfo'],params['host']+':ChtcRun/'])
	temp = subprocess.call(['ssh',params['host'],'cp %(pathToBinary)s ~/ChtcRun/%(expinfo)s/shared/%(cmdtorun)s' % params])

	temp = subprocess.call(['ssh',params['host'],'cd ChtcRun/; ./mkdag --cmdtorun=%(cmdtorun)s --data=%(expinfo)s --dagdir=%(expinfo)sout  --pattern=%(outPattern)s --type=Matlab' % params])
	return 0

def run(expinfo):
	params['expinfo']=expinfo
	subprocess.call(['ssh',params['host'],'cd ChtcRun/%(expinfo)sout/; condor_submit_dag mydag.dag' % params])
