
import sys
import time

class progressbar_t:
	def __init__(self, numMaxSteps):
		self.startTime		= time.time()
		self.lastTime			= time.time()
		self.numLines			= numMaxSteps
		self.numProcessed = 0

	def progress(self, tick=1):
		self.numProcessed += tick

		if time.time() - self.lastTime > 1:
			print >>sys.stderr, "  Processing... %.1f %% (%12d/%12d), %.1f sec.\r" % (1.0 * self.numProcessed / self.numLines * 100.0, self.numProcessed, self.numLines, time.time() - self.startTime),
			
			self.lastTime = time.time()
		
