#!/usr/bin/env python

import sys
sys.path.append("./config")
import sofa


def main():
    sofa.use('drpc.ver_1_0_0', 'S')
    sofa.use('nlpc.ver_1_0_0', 'nlpc')

    conf = sofa.Config()
    conf.load('./config/drpc_client.xml')

    #query_agent = S.ClientAgent(conf['sofa.service.nlpc_depparser_uni_query_107'])
    query_agent = S.ClientAgent(conf['sofa.service.nlpc_depparser_uni_web_107'])

    in_sentences = []

    while True:
        line = sys.stdin.readline()
        if len(line) <= 0:
            break
        line = line.strip(' \t\n\r')

        in_sentences.append(str(line))
        if len(in_sentences) < 1000:
            continue

        m_input = nlpc.depparser_uni_input()

        m_input.grain_size = 1
        m_input.sentence_segmented = False
        m_input.sentences = in_sentences

        input_data = sofa.serialize(m_input)

        for i in range(5):
            try:
                ret, output_data = query_agent.call_method(input_data)
                break
            except Exception as e:
                continue

        if len(output_data) == 0:
            stdout.write('No result' + '\n')
            continue

        m_output = nlpc.depparser_uni_output()
        m_output = sofa.deserialize(output_data, type(m_output))

        dep_sentences = m_output.dep_sentences
        sent_num = len(dep_sentences)
        for i in range(sent_num):
            dep_terms = dep_sentences[i].dep_terms
            term_num = len(dep_terms)
            for j in range(term_num):
                if dep_terms[j].lemma.strip() is None:
                    dep_terms[j].lemma = '_'
                if dep_terms[j].cpostag.strip() is None:
                    dep_terms[j].cpostag = '_'
                if dep_terms[j].postag.strip() is None:
                    dep_terms[j].postag = '_'
                if dep_terms[j].ner.strip() is None:
                    dep_terms[j].ner = '_'
                if dep_terms[j].feat.strip() is None:
                    dep_terms[j].feat = '_'
                if dep_terms[j].deprel.strip() is None:
                    dep_terms[j].deprel = '_'
                sys.stdout.write(str(j) + '\t' + dep_terms[j].word + '\t' + dep_terms[j].lemma + '\t' + dep_terms[j].cpostag + '\t' + dep_terms[j].postag + '\t' + dep_terms[j].ner + '\t' + dep_terms[j].feat + '\t' + str(dep_terms[j].head) + '\t' + dep_terms[j].deprel + '\n')
            sys.stdout.write('\n')
        in_sentences = []

    if len(in_sentences) > 0:
        m_input = nlpc.depparser_uni_input()

        m_input.grain_size = 1
        m_input.sentence_segmented = False
        m_input.sentences = in_sentences

        input_data = sofa.serialize(m_input)
        m_input.sentences = in_sentences
        input_data = sofa.serialize(m_input)

        for i in range(5):
            try:
                ret, output_data = query_agent.call_method(input_data)
                break
            except Exception as e:
                continue

        if len(output_data) == 0:
            stdout.write('No result' + '\n')
            exit

        m_output = nlpc.depparser_uni_output()
        m_output = sofa.deserialize(output_data, type(m_output))

        dep_sentences = m_output.dep_sentences
        sent_num = len(dep_sentences)
        for i in range(sent_num):
            dep_terms = dep_sentences[i].dep_terms
            term_num = len(dep_terms)
            for j in range(term_num):
                if dep_terms[j].lemma.strip() is None:
                    dep_terms[j].lemma = '_'
                if dep_terms[j].cpostag.strip() is None:
                    dep_terms[j].cpostag = '_'
                if dep_terms[j].postag.strip() is None:
                    dep_terms[j].postag = '_'
                if dep_terms[j].ner.strip() is None:
                    dep_terms[j].ner = '_'
                if dep_terms[j].feat.strip() is None:
                    dep_terms[j].feat = '_'
                if dep_terms[j].deprel.strip() is None:
                    dep_terms[j].deprel = '_'
                sys.stdout.write(str(j) + '\t' + dep_terms[j].word + '\t' + dep_terms[j].lemma + '\t' + dep_terms[j].cpostag + '\t' + dep_terms[j].postag + '\t' + dep_terms[j].ner + '\t' + dep_terms[j].feat + '\t' + str(dep_terms[j].head) + '\t' + dep_terms[j].deprel + '\n')
            sys.stdout.write('\n')
        in_sentences = []

if __name__ == '__main__':
    main()
