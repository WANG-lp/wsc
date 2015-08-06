#date:2014/12/24.
#purpose:to classify sentences into generic and non_generic.
def find_file(file_name):
    """
    input: file name.
    output: a string object of stanford xml.
    
    @param file_name: a string object.
    """
    import gzip
    file_name_form = '/home/work/data/ClueWeb12/clueweb12_parsed/stanford/%s.warc.gz.xmls.gz'
    file_xml = gzip.open(file_name_form % file_name, 'r')
    str_xml = file_xml.read()
    file_xml.close()
    return str_xml

def find_doc(str_xml, doc_id):
    """
    input: a string object of stanford xml and document id.
    output: a stanford xml file name for the document id.

    @param str_xml: a string object.
    @param doc_id: an intiger object.
    """
    import re
    doc_file_name = 'file_doc_xml'
    temp_file = open(doc_file_name, 'wb')#for saving the target document.
    lst_s_xml = re.split("<<XML_BEGIN\\n", str_xml)#lst_s_xml is like [doc1, doc2, ...].
    s_xml  = lst_s_xml[int(doc_id)]
    xml = re.split("<<XML_END\\n", s_xml)[0]
    temp_file.write(xml)
    temp_file.close()
    return doc_file_name

def find_sent_element(doc_file_name, sent_id):
    """
    input: a file name of stanford xml and sentence element id.
    output: a sentence element from ElementTree.

    @param doc_file_name: a string object.
    @param sent_id: an intiger object.
    """
    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        from xml.etree import ElementTree as ET

    tree = ET.ElementTree(file = doc_file_name)
    #print tree.findall('document/sentences/sentence')
    targ_sent_ele = tree.find('document/sentences/sentence[@id="%s"]'%str(sent_id))
    #print targ_sent_ele
    return targ_sent_ele

def construct_pos_pat(lst_pos, l_pos):
    """
    input: a list of pos and the length of a pos pattern(e.g., 2 for NN_VB).
    output: a list of  pos pattern like ['NN_VB', 'NN_NNP', ...].

    @param lst_pos: a list object.
    @param l_pos: an intiger object.
    """
    lst_posp = []#['NN_VB', 'NN_NNP', ...]
    l = len(lst_pos)
    for i in range(l - l_pos):
        lst_for_posp = lst_pos[i : i + l_pos]
        posp = '_'.join(lst_for_posp)
        lst_posp.append(posp)
    return lst_posp

def construct_fea(sent_ele):
    """
    input: a sentence element from stanford xml.
    output: ({features}, class).

    @param sent_ele: a sentence element from stanford xml.
    """
    import re
    pat = re.compile(r'[A-Z]')
    deps_type="collapsed-ccprocessed-dependencies"
    lst_v_types=['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    lst_n_types=['NN', 'NNS', 'NNP', 'NNPS']
    dic_w_lst_dep = {}
    dic_fea = {}#the dictionary of features like {'VBZ_VBG':True, ...}.
    dic_id_lem_pos = {}
    dic_id_lst_dep = {}
    lst_pos = []
    for tok_ele in sent_ele.findall('tokens/token'):
        tok_id = tok_ele.get('id')
        tok_lem = tok_ele.find('lemma').text
        tok_pos = tok_ele.find('POS').text
        dic_id_lem_pos[tok_id] = (tok_lem, tok_pos)
        lst_pos.append(tok_pos)
        #print tok_lem

    for dep_ele in sent_ele.findall('dependencies[@type="%s"]/dep'%deps_type):
        dep_type = dep_ele.get('type')
        gov_id = dep_ele.find('governor').get('idx')
        dep_id = dep_ele.find('dependent').get('idx')
        dic_id_lst_dep.setdefault(gov_id, []).append((dep_type, dep_id))

    lst_pos = [pos for pos in lst_pos if pat.match(pos)]    
    lst_posp = construct_pos_pat(lst_pos, 2)
    for posp in lst_posp:#ext
        dic_fea[posp] = True
        

    for tokid_lem_pos in dic_id_lem_pos.iteritems():
        tokid = tokid_lem_pos[0]
        lem = tokid_lem_pos[1][0]
        pos = tokid_lem_pos[1][1]

        if pos in lst_v_types:
            try:
                lst_dep = dic_id_lst_dep[tokid]
            except KeyError:
                continue
                
            for dty_depid in lst_dep:
                dty = dty_depid[0]
                depid = dty_depid[1]
                if dty in ['nsubj', 'agent']:
                    if pos == 'VBG':
                        dic_fea['Progressive'] = True
                    elif pos in['VBP','VBZ']:
                        dic_fea['Tense'] = 'present'
                    elif pos =='VBD':
                        dic_fea['Tense'] = 'past'
                    elif pos == 'VB':
                        dic_fea['Tense'] ='infinitive'
                        
                    subjpos = dic_id_lem_pos[depid][1]
                    if subjpos in ['NNS', 'NNPS']:
                        dic_fea['Plural_subj'] = True
                    elif subjpos in ['NN', 'NNP']:
                        dic_fea['Single_subj'] = True
                
                elif dty in ['dobj', 'nsubjpass', 'iobj']:
                    dic_fea['Present_obj'] = True
                    objpos = dic_id_lem_pos[depid][1]
                    if objpos in ['NNS', 'NNPS']:
                        dic_fea['Plural_obj'] = True
                    elif objpos in ['NN', 'NNP']:
                        dic_fea['Single_subj'] = True
                
                elif dty == 'aux':
                    auxlem = dic_id_lem_pos[depid][0]
                    if auxlem == 'have' and pos == 'VBN':
                        dic_fea['Perfect'] = True
                        lst_dep1 = dic_id_lst_dep[tokid]
                        for dty_depid1 in lst_dep1:
                            dty1 = dty_depid1[0]
                            deplem1 = dic_id_lem_pos[depid][0]
                            if dty1 == 'aux' and deplem1 in ['could', 'would', 'should']:
                                dic_fea['Conditional'] = True
                
                elif dty[:5] == 'prep_':
                    prep = dty[5:]
                    if prep == 'at':
                        dic_fea['at_pp'] = True
                    elif prep == 'in':
                        dic_fea['in_pp'] = True
                    elif prep == 'on':
                        dic_fea['on_pp'] = True
                
                elif dty == 'tmod':
                    dic_fea['Speci_temp'] = True
                
                elif dty == 'advmod':
                    advlem = dic_id_lem_pos[depid][0]
                    if advlem in ['always', 'usually', 'normally', 'generally', 'often', 'frequently',
                                  'sometimes', 'occasionally', 'seldom', 'hardly', 'rarely', 'never']:
                        dic_fea['Quant_temp'] = True

    return dic_fea

def train_classifier():
    """
    input: two list of trainig data and features of a sentence.
    output: a trained classifier of generic sentence.
    
    @param train_set_gen: a list object like [{features}, ...].
    @param train_set_ngen: a list object.
    @param dic_fea: a dictionary object expressing the features of a sentence.
    """
    import nltk
    import random 
    import marshal
    fle_train_set_gen = open('/home/jun-s/work/wsc/src/classify_gen/fea_set_for_gen', 'rb')
    fle_train_set_ngen = open('/home/jun-s/work/wsc/src/classify_gen/fea_set_for_ngen', 'rb')
    train_set_gen = marshal.load(fle_train_set_gen)
    train_set_ngen = marshal.load(fle_train_set_ngen)
    fle_train_set_gen.close()
    fle_train_set_ngen.close()
    train_set = train_set_gen + train_set_ngen
    random.shuffle(train_set)
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    return classifier

def classify_sent(classifier, filename_docid_sentid_tokid):
    # import sys
    filename, doc_id, sent_id, tok_id = filename_docid_sentid_tokid.split(':')
    sent_ele = find_sent_element(find_doc(find_file(filename), doc_id), sent_id)
    # print >>sys.stderr, "sent_ele = %s" %(sent_ele)
    fea = construct_fea(sent_ele)
    # print "fea = %s" %(fea)
    prob_gen = classifier.prob_classify(fea).prob('generic')
    # print >>sys.stderr, "prob_gen = %d" %(prob_gen)
    #print prob_gen
    return prob_gen

if __name__ == '__main__':
    import marshal
    import sys
    classifier  = train_classifier()
    
    for line in sys.stdin:
        lid = line.split(" ")[1]
        rid = line.split(" ")[3]

        lfilename, ldoc_id, lsent_id, ltid = lid.split(':')
        rfilename, rdoc_id, rsent_id, rtid = rid.split(':')

        # print lfilename, ldoc_id, lsent_id
        # print rfilename, rdoc_id, rsent_id

        if lsent_id != rsent_id:
            continue # only insent
            
            scorel = classify_sent(classifier, lid)
            scorer = classify_sent(classifier, rid)
            score = (scorel + scorer) / 2.0

        else:
            score = classify_sent(classifier, lid)
        score = 1.0
        sys.stdout.write("%s\t%s\n" % (lid, score))
    #     filename_docid_sentid_tid = sys.stdin()
    #     print filename_docid_sentid_tid
    # filename, doc_id, sent_id, tid = filename_docid_sentid_tid.split(':')
    # classifier  = train_classifier()
    # classify_sent(classifier, filename, doc_id, sent_id)
