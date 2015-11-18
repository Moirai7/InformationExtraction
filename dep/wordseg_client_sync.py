#!/usr/bin/env python


from sys import *
path.append("./config")
import sofa

def GET_TERM_POS(property):
    return ((property) & 0x00FFFFFF)

def GET_TERM_LEN(property):
    return ((property) >> 24)

def main():
    sofa.use('drpc.ver_1_0_0', 'S')
    sofa.use('nlpc.ver_1_0_0', 'wordseg')

    conf = sofa.Config()
    conf.load('./config/drpc_client.xml')

    wordseg_agent = S.ClientAgent(conf['sofa.service.nlpc_wordseg_3016'])

    while True:
        line = stdin.readline()
        if len(line) <= 0:
            return
	line = line.decode('utf-8').encode('gbk')
        m_input = wordseg.wordseg_input()
        
        m_input.query = str(line)
        m_input.lang_id = int(0)
        m_input.lang_para = int(0)

        input_data = sofa.serialize(m_input)

        for i in range(5) :
            try:
                ret, output_data = wordseg_agent.call_method(input_data)
		break
            except Exception as e:
                continue
        if len(output_data) == 0:
            stdout.write('No result' + '\n')
            continue

        m_output = wordseg.wordseg_output()
        m_output = sofa.deserialize(output_data, type(m_output))
        m_output = m_output.scw_out
        
        if len(argv) == 2 and argv[1] == 'basic' or len(argv) == 1:
            stdout.write('=========== Basic Word Sep Result =============' + '\n')
            for i in range(m_output.wsbtermcount):
                posidx = GET_TERM_POS(m_output.wsbtermpos[i])
                poslen = GET_TERM_LEN(m_output.wsbtermpos[i])
                word = m_output.wordsepbuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')

        if len(argv) == 2 and argv[1] == 'segment' or len(argv) == 1:
            stdout.write('============  Word Phrase Result  ==============' + '\n')
            for i in range(m_output.wpbtermcount):
                posidx = GET_TERM_POS(m_output.wpbtermpos[i])
                poslen = GET_TERM_LEN(m_output.wpbtermpos[i])
                word = m_output.wpcompbuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')

        if len(argv) == 2 and argv[1] == 'phrase' or len(argv) == 1:
            stdout.write('============  Sub Phrase Result   ==============' + '\n')
            for i in range(m_output.spbtermcount):
                posidx = GET_TERM_POS(m_output.spbtermpos[i])
                poslen = GET_TERM_LEN(m_output.spbtermpos[i])
                word = m_output.subphrbuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')

        if len(argv) == 2 and argv[1] == 'new' or len(argv) == 1:
            stdout.write('============  New Word  Result  ==============' + '\n')
            pnewword = m_output.pnewword
            for i in range(pnewword.newwordbtermcount):
                posidx = GET_TERM_POS(pnewword.newwordbtermpos[i])
                poslen = GET_TERM_LEN(pnewword.newwordbtermpos[i])
                word = pnewword.newwordbuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')

        if len(argv) == 2 and argv[1] == 'human' or len(argv) == 1:
            stdout.write('===========  Human Name Result   ==============' + '\n')
            for i in range(m_output.namebtermcount):
                posidx = GET_TERM_POS(m_output.namebtermpos[i])
                poslen = GET_TERM_LEN(m_output.namebtermpos[i])
                word = m_output.namebuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')

        if len(argv) == 2 and argv[1] == 'book' or len(argv) == 1:
            stdout.write('===============  book names   =================' + '\n')
            for i in range(m_output.bnbtermcount):
                posidx = GET_TERM_POS(m_output.bnbtermpos[i])
                poslen = GET_TERM_LEN(m_output.bnbtermpos[i])
                word = m_output.booknamebuf[posidx : posidx + poslen]
                stdout.write('%s ' %word)
            stdout.write('\n')



if __name__ == '__main__':
    main()
