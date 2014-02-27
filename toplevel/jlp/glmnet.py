import os, subprocess
# GLOBAL VARIABLES
EXPNAME="jlp+glmnet"
ValidParameters = ['Alpha','SparseVals','TargetCategory','MeanCenter','NormVariance']
args = {key: None for key in ValidParameters}
CommentChars = ["#","/"]

# UTILITIES
def nonblank_lines(f):
	for l in f:
		line = l.rstrip()
		if line:
			yield line

# CLASSES
class ExpObj:
	"""A object to interface with experiments."""
	def __init__(self,name,expnum,host,rdir,ldir,alpha,lam,targ,center,norm,njobs):
		self.Name = name
		self.ExpNum = expnum
		self.RemoteHost = host
		self.RemoteDir = rdir
		self.LocalDir = ldir
		self.Alpha = alpha
		self.SparseVals = lam
		self.TargetCategory = targ
		self.MeanCenter = center
		self.NormVariance = norm
		self.nJobs = njobs

	def run(self):
		args = ['nohup','ssh',self.RemoteHost,'cd %s ; matlab -r CondorSimulator' % self.RemoteDir]
		print 'executing '+' '.join(args)
		subprocess.call(args)
		
	def check(self):
		progress = subprocess.check_output(['ssh',self.RemoteHost,'find',self.RemoteDir, '-type f -name "jlp+glmnet_s??_cv??.mat" | wc -l'])
		print "%d out of %d jobs completed." % (int(progress),self.nJobs)

	def pull(self):
		os.mkdir(os.path.join(ldir,'Results'))
		args = ["rsync", "-avz", "--include", "*/", "--include", "*.mat", "--exclude", "*", "-e", "ssh"]
		args.append('%s:%s/ %s/Results/' % (self.RemoteHost,self.RemoteDir,self.LocalDir))
		print "executing "+' '.join(args)
		subprocess.call(args)
	
	def disp(self):
		for key,val in vars(self).items():
			print key,":",val

# FUNCTIONS
def parse(filename):
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
	ldir = os.path.join(os.getcwd(),expinfo)
	try:
		os.mkdir(ldir)
	except OSError:
		print "\nERROR: 'A project already exists for this expcode and number.\n"
		return 4

	os.mkdir(os.path.join(ldir,'shared'))

	# This experiment will have separate jobs for each Hold out set and subject.
	# Each job will do 9-fold CV over a set of lambda.
	ncv = 10;
	nsub = 10;
	njobs = ncv*nsub
	for i in range(ncv):
		for j in range(nsub):
			job = ((i*nsub) + j) + 1
			jobdir = '%03d' % job
			os.mkdir(os.path.join(ldir,jobdir))
			with open(os.path.join(ldir,jobdir,'WhichCV.txt'),'w') as f:
				f.write(str(i+1)+'\n')
			with open(os.path.join(ldir,jobdir,'WhichSubject.txt'),'w') as f:
				f.write(str(j+1)+'\n')
			with open(os.path.join(ldir,jobdir,'URLS'),'w') as f:
				f.write('/crcox/jlp%02d.mat\n' % (j+1))

	with open('%s/CondorSimulator.m' % expinfo,'w') as f:
		f.write("addpath('shared');\n")
		f.write("addpath('/data/crcox/utils/glmnet');\n")
		f.write("tic;\n");
		f.write("for i = 1:%d\n" % njobs)
		f.write("\tcopyfile(sprintf('%03d/*',i),'./');\n")
		f.write("\tmain();\n")
		f.write("end\n")
		f.write("h=fopen('DONE.txt','w');\n")
		f.write("fprintf(h,'Completed %d jobs in %.2f seconds.',100,toc);\n")
		f.write("fclose(h);\n")
		f.write("quit\n")
	
	for key,val in args.items():
		with open(os.path.join(ldir,'shared',str(key)+'.txt'),'w') as f:
			f.write(' '.join(val)+'\n')

	host = 'ccox@opt3'
	rdir = "/data/crcox/JLP/jlp+glmnet/Exp%02d" % int(expnum)
	subprocess.call(['rsync','-avz',expinfo+'/',host+':'+rdir+'/'])
	subprocess.call(['ssh',host,'ln -s /data/crcox/JLP/data/*.mat',rdir,';','cp /data/crcox/JLP/jlp+glmnet/src/*',rdir+'/shared/'])
	
	Exp = ExpObj(expname,expnum,host,rdir,ldir,args['Alpha'],args['SparseVals'],args['TargetCategory'],args['MeanCenter'],args['NormVariance'],njobs)
	return Exp
