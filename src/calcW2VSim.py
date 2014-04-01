import sys; sys.path+=["/home/naoya-i/work/wsc/"]
import cir

libcir = cir.test_cir_t("/work/naoya-i/kb/GoogleNews-vectors-negative300.bin", None, useMemoryMap=True)

# print libcir.calcContextualSimilarity("d:nsubj:Lakshman-n d:xcomp:get-v", "d:nsubj:Vivan-n d:aux:to-t d:xcomp:cream-n d:advcl:hot-j g:xcomp:ask-v")
print libcir.calcSlotSimilarity(sys.argv[1], sys.argv[2])
